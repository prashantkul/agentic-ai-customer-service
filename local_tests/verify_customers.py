#!/usr/bin/env python3
"""
Script to verify the database has customers and orders.
This is a non-interactive script that outputs database statistics.
"""

import sys
import logging
from pathlib import Path
from sqlalchemy import func
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    """Verify customers and orders in the database."""
    try:
        from database.models import (
            Session, Customer, Order, OrderItem, Product,
            Address, CommunicationPreferences, SportsProfile
        )
        
        session = Session()
        
        try:
            # Count customers
            customers = session.query(Customer).all()
            total_customers = len(customers)
            
            # Count orders
            orders = session.query(Order).all()
            total_orders = len(orders)
            
            # Count order items
            total_order_items = session.query(OrderItem).count()
            
            # Calculate average order value
            if total_orders > 0:
                avg_order_value = session.query(func.avg(Order.total)).scalar() or 0
            else:
                avg_order_value = 0
            
            # Calculate total revenue
            total_revenue = session.query(func.sum(Order.total)).scalar() or 0
            
            # Display database statistics
            print("\n" + "=" * 60)
            print("📊 BETTERSALE DATABASE STATISTICS 📊".center(60))
            print("=" * 60)
            
            print(f"\nTotal Customers: {total_customers}")
            print(f"Total Orders: {total_orders}")
            print(f"Total Order Items: {total_order_items}")
            print(f"Average Order Value: ${avg_order_value:.2f}")
            print(f"Total Revenue: ${total_revenue:.2f}")
            
            # Count orders by status
            print("\nOrders by Status:")
            statuses = session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
            for status, count in statuses:
                print(f"  {status}: {count}")
            
            # List all customers (first 10 only if more than 10)
            print("\nCustomers:")
            for i, customer in enumerate(customers[:10], 1):
                print(f"{i}. {customer.first_name} {customer.last_name} (ID: {customer.id})")
                print(f"   Email: {customer.email}")
                print(f"   Loyalty Points: {customer.loyalty_points}")
                
                # Count orders for this customer
                customer_orders = session.query(Order).filter(Order.customer_id == customer.id).count()
                print(f"   Orders: {customer_orders}")
                print()
                
            if total_customers > 10:
                print(f"...and {total_customers - 10} more customers")
            
            # List most recent orders (first 5 only)
            print("\nMost Recent Orders:")
            recent_orders = session.query(Order).order_by(Order.order_date.desc()).limit(5).all()
            
            for i, order in enumerate(recent_orders, 1):
                # Get customer name
                customer = session.query(Customer).filter(Customer.id == order.customer_id).first()
                customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
                
                print(f"{i}. Order {order.id}")
                print(f"   Date: {order.order_date.strftime('%Y-%m-%d')}")
                print(f"   Customer: {customer_name}")
                print(f"   Total: ${order.total:.2f}")
                print(f"   Status: {order.status}")
                
                # List items in the order
                order_items = session.query(OrderItem, Product).join(
                    Product, OrderItem.product_id == Product.id
                ).filter(OrderItem.order_id == order.id).all()
                
                if order_items:
                    print("   Items:")
                    for j, (order_item, product) in enumerate(order_items, 1):
                        print(f"     {j}. {product.name} - Qty: {order_item.quantity}, Price: ${order_item.price:.2f}")
                
                print()
                
            # Verify there are cart items
            cart_items_count = session.query(session.query(CartItem).distinct(CartItem.customer_id).subquery()).count()
            print(f"\nCustomers with items in cart: {cart_items_count}")
            
            print("\n✅ Database verification complete!")
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
        finally:
            session.close()
            
    except ImportError as e:
        logger.error(f"Error importing database modules: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        from database.models import CartItem
        main()
    except Exception as e:
        logger.error(f"Error running verification: {e}")
        sys.exit(1)