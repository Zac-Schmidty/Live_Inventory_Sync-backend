from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from . import crud

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_inventory_metrics(db: Session) -> Dict[str, Any]:
    """Calculate various inventory metrics"""
    try:
        all_products = crud.get_products(db)
        
        total_items = sum(product.inventory for product in all_products)
        low_stock_items = len(crud.get_low_inventory_products(db, threshold=10))
        out_of_stock = len([p for p in all_products if p.inventory == 0])
        
        return {
            "total_inventory": total_items,
            "low_stock_count": low_stock_items,
            "out_of_stock_count": out_of_stock,
            "total_products": len(all_products)
        }
    except Exception as e:
        logger.error(f"Error calculating inventory metrics: {str(e)}")
        return {
            "error": "Failed to calculate inventory metrics",
            "details": str(e)
        }

def check_sync_health(db: Session) -> Dict[str, Any]:
    """Check the health of sync operations"""
    try:
        products = crud.get_products(db)
        current_time = datetime.utcnow()
        
        # Check for products not synced in last hour
        stale_products = [
            p for p in products 
            if p.last_synced < current_time - timedelta(hours=1)
        ]
        
        return {
            "status": "healthy" if len(stale_products) == 0 else "warning",
            "stale_products_count": len(stale_products),
            "last_check": current_time.isoformat(),
            "total_products_checked": len(products)
        }
    except Exception as e:
        logger.error(f"Error checking sync health: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def format_error_response(error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """Standardize error response format"""
    return {
        "status": "error",
        "error": str(error),
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_inventory_threshold(value: int) -> bool:
    """Validate inventory threshold values"""
    return 0 <= value <= 1000  # Arbitrary max value

def get_product_status(inventory: int) -> str:
    """Determine product status based on inventory level"""
    if inventory <= 0:
        return "out_of_stock"
    elif inventory <= 10:
        return "low_stock"
    else:
        return "in_stock"
