from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    shopify_id: str
    title: str
    inventory: int
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    previous_inventory: int
    inventory_change: int
    last_synced: datetime

    class Config:
        from_attributes = True

class WebhookInventoryUpdate(BaseModel):
    product_id: str
    inventory: int
    title: Optional[str] = None
