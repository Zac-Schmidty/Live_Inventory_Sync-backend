from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_shopify_id(db: Session, shopify_id: str) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.shopify_id == shopify_id).first()

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate, initial_inventory: int = 0) -> models.Product:
    db_product = models.Product(
        **product.model_dump(),
        previous_inventory=initial_inventory,
        inventory_change=0
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(
    db: Session, 
    product_id: int, 
    product_data: dict
) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db_product.last_synced = datetime.utcnow()
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def get_low_inventory_products(
    db: Session, 
    threshold: int = 10
) -> List[models.Product]:
    return db.query(models.Product).filter(
        models.Product.inventory <= threshold
    ).all() 