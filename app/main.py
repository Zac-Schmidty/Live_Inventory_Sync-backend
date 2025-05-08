from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, utils
from .database import SessionLocal, engine
from .webhook_routes import router as webhook_router
from .sync_jobs import get_sync_service, MockShopifySync

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopify Sync API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
@app.post("/sync/trigger", tags=["sync"])
async def trigger_sync(db: Session = Depends(get_db)):
    """Manually trigger a sync with Shopify"""
    sync_service = get_sync_service()
    result = await sync_service.sync_products(db)
    return result

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
