#!/usr/bin/env python3
"""
Script to test the cart functionality.
"""

import logging
from customer_service.database.operations import access_cart_information, modify_cart

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cart():
    """Test accessing and modifying the cart."""
    customer_id = "CUST-80CA281C"
    
    # Access cart
    logger.info(f"Accessing cart for customer {customer_id}")
    cart = access_cart_information(customer_id)
    logger.info(f"Cart contents: {cart}")
    
    # Add an item to the cart
    logger.info(f"Adding item to cart for customer {customer_id}")
    items_to_add = [{"product_id": "TNB-003", "quantity": 1}]
    items_to_remove = []
    result = modify_cart(customer_id, items_to_add, items_to_remove)
    logger.info(f"Modify cart result: {result}")
    
    # Access cart again to verify
    logger.info(f"Accessing cart again for customer {customer_id}")
    updated_cart = access_cart_information(customer_id)
    logger.info(f"Updated cart contents: {updated_cart}")

if __name__ == "__main__":
    test_cart()