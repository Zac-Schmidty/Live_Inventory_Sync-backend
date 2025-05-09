from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from . import schemas
import random
from datetime import datetime

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

# Mock product data
mock_products = [
    {
        "shopify_id": "mock_001",
        "title": "Classic T-Shirt",
        "inventory": random.randint(0, 100),
        "price": 29.99
    },
    {
        "shopify_id": "mock_002",
        "title": "Vintage Jeans",
        "inventory": random.randint(0, 50),
        "price": 89.99
    },
    {
        "shopify_id": "mock_003",
        "title": "Running Shoes",
        "inventory": random.randint(0, 30),
        "price": 119.99
    },
    {
        "shopify_id": "mock_004",
        "title": "Summer Dress",
        "inventory": random.randint(5, 75),
        "price": 69.99
    },
    {
        "shopify_id": "mock_005",
        "title": "Leather Wallet",
        "inventory": random.randint(10, 200),
        "price": 49.99
    },
    {
        "shopify_id": "mock_006",
        "title": "Sunglasses",
        "inventory": random.randint(0, 150),
        "price": 159.99
    },
    {
        "shopify_id": "mock_007",
        "title": "Backpack",
        "inventory": random.randint(5, 50),
        "price": 79.99
    },
    {
        "shopify_id": "mock_008",
        "title": "Watch",
        "inventory": random.randint(0, 25),
        "price": 299.99
    },
    {
        "shopify_id": "mock_009",
        "title": "Sneakers",
        "inventory": random.randint(10, 100),
        "price": 89.99
    },
    {
        "shopify_id": "mock_010",
        "title": "Baseball Cap",
        "inventory": random.randint(20, 200),
        "price": 24.99
    }
]

def populate_db():
    db = SessionLocal()
    try:
        # Clear existing products
        db.query(models.Product).delete()
        
        # Add new products
        for product_data in mock_products:
            product = models.Product(
                shopify_id=product_data["shopify_id"],
                title=product_data["title"],
                inventory=product_data["inventory"],
                price=product_data["price"],
                last_synced=datetime.utcnow()
            )
            db.add(product)
        
        db.commit()
        print(f"Successfully added {len(mock_products)} products to the database!")
        
        # Print out the products for verification
        products = db.query(models.Product).all()
        for product in products:
            print(f"Added: {product.title} - Inventory: {product.inventory}, Price: ${product.price}")
            
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_db() 