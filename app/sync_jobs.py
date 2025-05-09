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
                "id": "840080123456",  # 12-digit UPC format
                "title": "Classic T-Shirt",
                "inventory_quantity": random.randint(0, 100),
                "price": 29.99
            },
            {
                "id": "840080123457",
                "title": "Vintage Jeans",
                "inventory_quantity": random.randint(0, 50),
                "price": 89.99
            },
            {
                "id": "840080123458",
                "title": "Running Shoes",
                "inventory_quantity": random.randint(0, 30),
                "price": 119.99
            },
            {
                "id": "840080123459",
                "title": "Summer Dress",
                "inventory_quantity": random.randint(5, 75),
                "price": 69.99
            },
            {
                "id": "840080123460",
                "title": "Leather Wallet",
                "inventory_quantity": random.randint(10, 200),
                "price": 49.99
            },
            {
                "id": "840080123461",
                "title": "Designer Sunglasses",
                "inventory_quantity": random.randint(0, 150),
                "price": 159.99
            },
            {
                "id": "840080123462",
                "title": "Travel Backpack",
                "inventory_quantity": random.randint(5, 50),
                "price": 79.99
            },
            {
                "id": "840080123463",
                "title": "Smart Watch",
                "inventory_quantity": random.randint(0, 25),
                "price": 299.99
            },
            {
                "id": "840080123464",
                "title": "Athletic Sneakers",
                "inventory_quantity": random.randint(10, 100),
                "price": 89.99
            },
            {
                "id": "840080123465",
                "title": "Baseball Cap",
                "inventory_quantity": random.randint(20, 200),
                "price": 24.99
            },
            {
                "id": "840080123466",
                "title": "Yoga Mat",
                "inventory_quantity": random.randint(15, 80),
                "price": 39.99
            },
            {
                "id": "840080123467",
                "title": "Wireless Earbuds",
                "inventory_quantity": random.randint(5, 60),
                "price": 129.99
            },
            {
                "id": "840080123468",
                "title": "Coffee Maker",
                "inventory_quantity": random.randint(8, 40),
                "price": 199.99
            },
            {
                "id": "840080123469",
                "title": "Desk Lamp",
                "inventory_quantity": random.randint(12, 90),
                "price": 45.99
            },
            {
                "id": "840080123470",
                "title": "Water Bottle",
                "inventory_quantity": random.randint(30, 150),
                "price": 19.99
            },
            {
                "id": "840080123471",
                "title": "Gaming Mouse",
                "inventory_quantity": random.randint(10, 70),
                "price": 79.99
            },
            {
                "id": "840080123472",
                "title": "Portable Charger",
                "inventory_quantity": random.randint(20, 120),
                "price": 34.99
            },
            {
                "id": "840080123473",
                "title": "Bluetooth Speaker",
                "inventory_quantity": random.randint(5, 45),
                "price": 89.99
            },
            {
                "id": "840080123474",
                "title": "Plant Pot Set",
                "inventory_quantity": random.randint(15, 60),
                "price": 29.99
            },
            {
                "id": "840080123475",
                "title": "Kitchen Knife Set",
                "inventory_quantity": random.randint(8, 35),
                "price": 149.99
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
                    # Calculate inventory change
                    new_inventory = product_data.inventory
                    old_inventory = existing_product.inventory
                    inventory_change = new_inventory - old_inventory

                    # Update existing product
                    crud.update_product(
                        db,
                        existing_product.id,
                        {
                            "title": product_data.title,
                            "inventory": new_inventory,
                            "previous_inventory": old_inventory,
                            "inventory_change": inventory_change,
                            "price": product_data.price
                        }
                    )
                    updates += 1
                else:
                    # Create new product with no change (first entry)
                    crud.create_product(
                        db, 
                        product_data,
                        initial_inventory=product_data.inventory
                    )
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
