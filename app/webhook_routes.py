from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal
import hmac
import hashlib
import os

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_webhook_signature(body: bytes, signature: str) -> bool:
    secret = os.getenv("SHOPIFY_WEBHOOK_SECRET")
    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(signature, digest.hex())

@router.post("/inventory-update")
async def handle_inventory_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(...),
    db: Session = Depends(get_db)
):
    # Verify webhook signature
    body = await request.body()
    if not verify_webhook_signature(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    payload = await request.json()
    update = schemas.WebhookInventoryUpdate(
        product_id=str(payload.get("id")),
        inventory=payload.get("inventory_quantity", 0),
        title=payload.get("title")
    )

    try:
        # Check if product exists
        existing_product = crud.get_product_by_shopify_id(db, update.product_id)
        
        if existing_product:
            # Update existing product
            updated_product = crud.update_product(
                db,
                existing_product.id,
                {
                    "inventory": update.inventory,
                    "title": update.title if update.title else existing_product.title
                }
            )
            return {
                "status": "success",
                "message": "Product updated",
                "product_id": updated_product.shopify_id
            }
        else:
            # Create new product
            new_product = crud.create_product(
                db,
                schemas.ProductCreate(
                    shopify_id=update.product_id,
                    title=update.title or "Unknown Product",
                    inventory=update.inventory,
                    price=0.0  # Default price, should be updated via sync
                )
            )
            return {
                "status": "success",
                "message": "Product created",
                "product_id": new_product.shopify_id
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process inventory update: {str(e)}"
        )


