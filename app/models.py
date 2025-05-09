from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped
from .database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    shopify_id = Column(String, unique=True, index=True)
    title = Column(String)
    inventory = Column(Integer, default=0)
    previous_inventory = Column(Integer, default=0)
    inventory_change = Column(Integer, default=0)
    price = Column(Float)
    last_synced = Column(DateTime, default=datetime.utcnow)
