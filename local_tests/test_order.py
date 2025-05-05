#!/usr/bin/env python3
"""
Test script for creating an order.
"""

import logging
from customer_service.database.operations import modify_cart, create_order, access_cart_information

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_order_process():
    """Test the complete order process."""
    customer_id = "CUST-80CA281C"
    
    # First, make sure the cart is empty
    logger.info(f"Checking initial cart for customer {customer_id}")
    initial_cart = access_cart_information(customer_id)
    logger.info(f"Initial cart: {initial_cart}")
    
    # Add an item to the cart
    logger.info(f"Adding items to cart for customer {customer_id}")
    items_to_add = [
        {"product_id": "TNB-003", "quantity": 1},
        {"product_id": "RUN-S05", "quantity": 1}
    ]
    items_to_remove = []
    cart_result = modify_cart(customer_id, items_to_add, items_to_remove)
    logger.info(f"Cart modification result: {cart_result}")
    
    # Check the updated cart
    logger.info(f"Checking updated cart for customer {customer_id}")
    updated_cart = access_cart_information(customer_id)
    logger.info(f"Updated cart: {updated_cart}")
    
    # Create an order
    logger.info(f"Creating order for customer {customer_id}")
    order_result = create_order(customer_id)
    logger.info(f"Order creation result: {order_result}")
    
    # Check that the cart is empty after order creation
    logger.info(f"Checking cart after order for customer {customer_id}")
    final_cart = access_cart_information(customer_id)
    logger.info(f"Final cart: {final_cart}")

if __name__ == "__main__":
    test_order_process()