#!/usr/bin/env python3
"""
Script to verify the database content.
Shows customer and order statistics.
"""

import sys
import logging
from sqlalchemy import func
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    """Verify database contents."""
    try:
        from customer_service.database.models import (
            Session, Customer, Order, OrderItem, Product, CartItem
        )
        
        # Ensure the database is set up but don't reset it
        from database.init_db import ensure_tables_exist
        ensure_tables_exist()
        
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
            
            # Count products
            total_products = session.query(Product).count()
            
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
            print(f"Total Products: {total_products}")
            print(f"Total Orders: {total_orders}")
            print(f"Total Order Items: {total_order_items}")
            print(f"Average Order Value: ${avg_order_value:.2f}")
            print(f"Total Revenue: ${total_revenue:.2f}")
            
            # Count orders by status
            print("\nOrders by Status:")
            statuses = session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
            for status, count in statuses:
                print(f"  {status}: {count}")
            
            # Count customers by sports preference
            try:
                print("\nCustomers by Preferred Sport:")
                from database.models import SportsProfile
                
                sports_profiles = session.query(SportsProfile).all()
                sport_counts = {}
                
                for profile in sports_profiles:
                    if not profile.preferred_sports:
                        continue
                        
                    sports = profile.preferred_sports
                    if isinstance(sports, str):
                        try:
                            sports = json.loads(sports)
                        except json.JSONDecodeError:
                            continue
                    
                    for sport in sports:
                        sport_counts[sport] = sport_counts.get(sport, 0) + 1
                
                for sport, count in sorted(sport_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {sport}: {count}")
            except Exception as e:
                logger.error(f"Error processing sports preferences: {e}")
            
            # Count customers with items in cart
            cart_counts = session.query(CartItem.customer_id, func.count(CartItem.id)).group_by(CartItem.customer_id).all()
            customers_with_cart = len(cart_counts)
            cart_items = sum(count for _, count in cart_counts)
            
            print(f"\nCustomers with items in cart: {customers_with_cart}")
            print(f"Total items in carts: {cart_items}")
            
            # Display top 5 customers with highest total order value
            print("\nTop 5 Customers by Order Value:")
            top_customers = session.query(
                Customer,
                func.sum(Order.total).label('total_spent')
            ).join(Order).group_by(Customer).order_by(func.sum(Order.total).desc()).limit(5).all()
            
            for i, (customer, total) in enumerate(top_customers, 1):
                print(f"{i}. {customer.first_name} {customer.last_name} - ${total:.2f}")
                # Count orders for this customer
                order_count = session.query(Order).filter(Order.customer_id == customer.id).count()
                print(f"   Orders: {order_count}")
            
            # Show recent activity
            print("\nRecent Orders:")
            recent_orders = session.query(Order).order_by(Order.order_date.desc()).limit(3).all()
            
            for order in recent_orders:
                customer = session.query(Customer).filter(Customer.id == order.customer_id).first()
                print(f"Order {order.id} - {order.order_date.strftime('%Y-%m-%d')} by {customer.first_name} {customer.last_name}")
                print(f"Status: {order.status}, Total: ${order.total:.2f}")
            
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
        main()
    except Exception as e:
        logger.error(f"Error running verification: {e}")
        sys.exit(1)
