from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, utils
from .database import SessionLocal, engine
from .webhook_routes import router as webhook_router
from .sync_jobs import get_sync_service, MockShopifySync
from fastapi.responses import JSONResponse

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopify Sync API")

# Updated CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://live-inventory.xyz", "http://localhost:3000"],  # For development, update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=[
        "strict-origin-when-cross-origin",
        "content-type",
        "authorization",
        "access-control-allow-origin",
        "access-control-allow-methods",
        "access-control-allow-headers",
        "*"
    ],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include webhook routes
app.include_router(webhook_router, prefix="/webhook", tags=["webhooks"])

# Product endpoints
@app.get("/products/", response_model=List[schemas.Product], tags=["products"])
async def read_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product, tags=["products"])
async def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Sync endpoints
@app.options("/sync/trigger")
async def sync_options():
    return {}  # Return empty response for OPTIONS request

@app.post("/sync/trigger")
async def trigger_sync(request: Request, db: Session = Depends(get_db)):
    """Manually trigger a sync with Shopify"""
    try:
        sync_service = get_sync_service()
        result = await sync_service.sync_products(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync/status", tags=["sync"])
async def get_sync_status(db: Session = Depends(get_db)):
    """Get current sync status"""
    sync_service = get_sync_service()
    return await sync_service.get_sync_status(db)

# Metrics and monitoring endpoints
@app.get("/metrics/inventory", tags=["metrics"])
async def get_inventory_metrics(db: Session = Depends(get_db)):
    """Get inventory metrics"""
    return utils.calculate_inventory_metrics(db)

@app.get("/health", tags=["monitoring"])
async def check_health(db: Session = Depends(get_db)):
    """Check system health including sync status"""
    return utils.check_sync_health(db)

@app.get("/products/low-stock", response_model=List[schemas.Product], tags=["products"])
async def get_low_stock_products(
    threshold: int = 10, 
    db: Session = Depends(get_db)
):
    """Get products with low inventory"""
    return crud.get_low_inventory_products(db, threshold=threshold)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
