from sqlalchemy.orm import Session
from datetime import datetime
import random
from . import models, schemas, crud
from typing import List, Dict, Any

class MockShopifySync:
    def __init__(self):
        # Mock product data for simulation
        self.mock_products = [
            {
                "id": "mock_001",
                "title": "Classic T-Shirt",
                "inventory_quantity": random.randint(0, 100),
                "price": 29.99
            },
            {
                "id": "mock_002",
                "title": "Vintage Jeans",
                "inventory_quantity": random.randint(0, 50),
                "price": 89.99
            },
            {
                "id": "mock_003",
                "title": "Running Shoes",
                "inventory_quantity": random.randint(0, 30),
                "price": 119.99
            }
        ]

    async def fetch_products(self) -> List[Dict[Any, Any]]:
        """Mock fetching products from Shopify API"""
        # Randomly modify inventory levels to simulate changes
        for product in self.mock_products:
            product["inventory_quantity"] = random.randint(0, 100)
        return self.mock_products

    async def sync_products(self, db: Session) -> Dict[str, Any]:
        """Sync mock products to local database using CRUD operations"""
        try:
            products = await self.fetch_products()
            updates = 0
            creates = 0
            
            for mock_product in products:
                # Convert mock data to ProductCreate schema
                product_data = schemas.ProductCreate(
                    shopify_id=str(mock_product["id"]),
                    title=mock_product["title"],
                    inventory=mock_product["inventory_quantity"],
                    price=float(mock_product["price"])
                )

                # Check if product exists
                existing_product = crud.get_product_by_shopify_id(
                    db, 
                    product_data.shopify_id
                )

                if existing_product:
                    # Update existing product
                    crud.update_product(
                        db,
                        existing_product.id,
                        product_data.model_dump()
                    )
                    updates += 1
                else:
                    # Create new product
                    crud.create_product(db, product_data)
                    creates += 1

            return {
                "status": "success",
                "products_updated": updates,
                "products_created": creates,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_sync_status(self, db: Session) -> Dict[str, Any]:
        """Get current sync status and product counts"""
        try:
            total_products = len(crud.get_products(db))
            low_inventory = len(crud.get_low_inventory_products(db, threshold=10))
            
            return {
                "status": "success",
                "total_products": total_products,
                "low_inventory_count": low_inventory,
                "last_sync": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

def get_sync_service() -> MockShopifySync:
    """Dependency injection for mock sync service"""
    return MockShopifySync()
