#!/usr/bin/env python3
"""
Test script to verify the database-backed implementation.
This script checks:
1. Database initialization
2. Database operations
3. Tool functionality with the database backend
"""

import logging
import json
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run tests for the database-backed implementation."""
    logger.info("Testing database implementation...")
    
    # Step 1: Initialize database
    logger.info("Step 1: Initialize database")
    try:
        from database.init_db import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
    
    # Step 2: Test database operations
    logger.info("\nStep 2: Testing database operations")
    try:
        # Get customer
        from database.operations import get_customer
        customer = get_customer("123")
        if not customer:
            raise ValueError("Customer not found")
        logger.info(f"✅ Customer found: {customer['customer_first_name']} {customer['customer_last_name']}")
        
        # Access cart
        from database.operations import access_cart_information
        cart = access_cart_information("123")
        if not cart or "cart" not in cart:
            raise ValueError("Cart information not found")
        logger.info(f"✅ Cart accessed successfully with {len(cart['cart'])} items")
        
        # Get product recommendations
        from database.operations import get_product_recommendations
        recommendations = get_product_recommendations("Tennis", "123")
        if not recommendations or "recommendations" not in recommendations:
            raise ValueError("Product recommendations not found")
        logger.info(f"✅ Product recommendations found: {len(recommendations['recommendations'])} items")
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        sys.exit(1)
    
    # Step 3: Test database tools
    logger.info("\nStep 3: Testing database tools")
    try:
        # Access cart tool
        from customer_service_db.db_tools import access_cart_information as db_tool_access_cart
        cart = db_tool_access_cart("123")
        if not cart or "cart" not in cart:
            raise ValueError("Cart information not found via tool")
        logger.info(f"✅ Cart tool accessed successfully with {len(cart['cart'])} items")
        
        # Get product recommendations tool
        from customer_service_db.db_tools import get_product_recommendations as db_tool_get_recommendations
        recommendations = db_tool_get_recommendations("Tennis", "123")
        if not recommendations or "recommendations" not in recommendations:
            raise ValueError("Product recommendations not found via tool")
        logger.info(f"✅ Product recommendations tool found: {len(recommendations['recommendations'])} items")
        
        # Modify cart tool (add item)
        from customer_service_db.db_tools import modify_cart as db_tool_modify_cart
        result = db_tool_modify_cart(
            "123", 
            [{"product_id": "TNB-003", "quantity": 1}],  # Add tennis balls
            []
        )
        if not result or result.get("status") != "success":
            raise ValueError(f"Failed to modify cart: {result}")
        logger.info(f"✅ Cart modification successful: {result['message']}")
        
        # Check cart after modification
        cart = db_tool_access_cart("123")
        logger.info(f"✅ Updated cart has {len(cart['cart'])} items")
        
    except Exception as e:
        logger.error(f"❌ Database tools test failed: {e}")
        sys.exit(1)
    
    # Success message
    logger.info("\n✅✅✅ Database implementation tests completed successfully!")
    logger.info("""
Next steps:
1. Run the database-backed agent and Streamlit app with:
   python deployment/deploy_db.py --local-only

2. Deploy to Cloud Run with:
   python deployment/deploy_db.py --project YOUR_PROJECT_ID
    """)

if __name__ == "__main__":
    main()