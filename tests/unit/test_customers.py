"""
Test script to browse and search the customer database.
This script provides a simple command-line interface to explore the customers
and their order history without needing to run the ADK agent.
"""

import sys
import logging
from pathlib import Path
import random
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add project root directory to path to allow imports
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from customer_service.database.models import (
        Session, Customer, Order, OrderItem, Product,
        Address, CommunicationPreferences, SportsProfile
    )
    from customer_service.database.init_db import init_db, ensure_tables_exist
    from customer_service.database.operations import (
        get_customer, 
        access_cart_information
    )
except ImportError as e:
    logger.error(f"Error importing database modules: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def ensure_database():
    """Ensure the database exists and has data."""
    try:
        # Initialize the database if needed, but preserve existing data
        ensure_tables_exist()  # This only creates tables if they don't exist
        
        # Check if we have at least one customer
        session = Session()
        customer_count = session.query(Customer).count()
        session.close()
        
        # If no customers, initialize with sample data
        if customer_count == 0:
            init_db(clear_existing=False)
            logger.info("Database initialized with sample data.")
        else:
            logger.info(f"Database already contains {customer_count} customers.")
            
        return True
    except Exception as e:
        logger.error(f"Error ensuring database: {e}")
        return False

def list_customers():
    """List all customers in the database."""
    session = Session()
    try:
        customers = session.query(Customer).all()
        print(f"\n👥 Found {len(customers)} customers:\n")
        
        for i, customer in enumerate(customers, 1):
            print(f"{i}. {customer.first_name} {customer.last_name}")
            print(f"   ID: {customer.id}")
            print(f"   Email: {customer.email}")
            print(f"   Loyalty Points: {customer.loyalty_points}")
            print(f"   Customer Since: {customer.customer_start_date}")
            print()
            
        return len(customers)
    finally:
        session.close()

def view_customer_details(customer_id=None):
    """View details for a specific customer."""
    if not customer_id:
        print("\nEnter customer ID or enter a number to select from the list:")
        choice = input("> ").strip()
        
        if not choice:
            print("No customer ID entered")
            return
            
        # If input is numeric, get customer by index
        if choice.isdigit():
            session = Session()
            try:
                customers = session.query(Customer).all()
                idx = int(choice) - 1
                if idx < 0 or idx >= len(customers):
                    print("Invalid customer index")
                    return
                customer_id = customers[idx].id
            finally:
                session.close()
        else:
            customer_id = choice
    
    try:
        # Get customer details
        customer_data = get_customer(customer_id)
        
        if not customer_data:
            print(f"\nCustomer with ID {customer_id} not found")
            return
        
        # Display customer information
        print("\n" + "=" * 60)
        print(f"👤 Customer Profile: {customer_data['customer_first_name']} {customer_data['customer_last_name']}")
        print("=" * 60)
        print(f"Customer ID: {customer_data['customer_id']}")
        print(f"Account Number: {customer_data['account_number']}")
        print(f"Email: {customer_data['email']}")
        print(f"Phone: {customer_data['phone_number']}")
        print(f"Customer Since: {customer_data['customer_start_date']} ({customer_data['years_as_customer']} years)")
        print(f"Loyalty Points: {customer_data['loyalty_points']}")
        print(f"Preferred Store: {customer_data['preferred_store']}")
        
        # Display address
        if 'billing_address' in customer_data:
            address = customer_data['billing_address']
            if address and any(address.values()):
                print("\n📍 Billing Address:")
                print(f"{address.get('street', '')}")
                print(f"{address.get('city', '')}, {address.get('state', '')} {address.get('zip', '')}")
        
        # Display sports profile
        if 'sports_profile' in customer_data:
            sports = customer_data['sports_profile']
            if sports:
                print("\n🏀 Sports Profile:")
                
                preferred_sports = sports.get('preferred_sports', [])
                if isinstance(preferred_sports, str):
                    try:
                        preferred_sports = json.loads(preferred_sports)
                    except json.JSONDecodeError:
                        preferred_sports = []
                        
                if preferred_sports:
                    print(f"Preferred Sports: {', '.join(preferred_sports)}")
                
                skill_level = sports.get('skill_level', {})
                if isinstance(skill_level, str):
                    try:
                        skill_level = json.loads(skill_level)
                    except json.JSONDecodeError:
                        skill_level = {}
                        
                if skill_level:
                    print("Skill Levels:")
                    for sport, level in skill_level.items():
                        print(f"  - {sport}: {level}")
                
                activity_frequency = sports.get('activity_frequency', '')
                if activity_frequency:
                    print(f"Activity Frequency: {activity_frequency}")
        
        # Get cart contents
        try:
            cart_data = access_cart_information(customer_id)
            cart_items = cart_data.get("cart", [])
            
            if cart_items:
                print("\n🛒 Current Cart:")
                for i, item in enumerate(cart_items, 1):
                    print(f"  {i}. {item.get('name', 'Unknown')} - Qty: {item.get('quantity', 0)}")
                print(f"Subtotal: ${cart_data.get('subtotal', 0):.2f}")
            else:
                print("\n🛒 Cart is empty")
        except Exception as e:
            logger.error(f"Error accessing cart: {e}")
        
        # Display purchase history
        purchase_history = customer_data.get('purchase_history', [])
        if purchase_history:
            print("\n🛍️ Purchase History:")
            for i, purchase in enumerate(purchase_history, 1):
                print(f"Order {i} - Date: {purchase.get('date', 'Unknown')}")
                for item in purchase.get('items', []):
                    print(f"  - {item.get('name', 'Unknown Product')} (Qty: {item.get('quantity', 0)})")
                print(f"  Total: ${purchase.get('total_amount', 0):.2f}")
                print()
        else:
            print("\n🛍️ No purchase history")
        
    except Exception as e:
        logger.error(f"Error getting customer details: {e}")
        print(f"\n❌ Error retrieving customer details: {e}")

def display_order_details(order_id):
    """Display detailed information about an order."""
    session = Session()
    try:
        # Get order
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            print(f"Order {order_id} not found")
            return
            
        # Get customer
        customer = session.query(Customer).filter(Customer.id == order.customer_id).first()
        
        # Get order items with product details
        order_items = session.query(OrderItem, Product).join(
            Product, OrderItem.product_id == Product.id
        ).filter(OrderItem.order_id == order_id).all()
        
        # Display order details
        print("\n" + "=" * 60)
        print(f"📦 Order Details: {order.id}".center(60))
        print("=" * 60)
        
        print(f"Date: {order.order_date.strftime('%Y-%m-%d')}")
        print(f"Status: {order.status}")
        print(f"Customer: {customer.first_name} {customer.last_name} ({order.customer_id})")
        print(f"Total: ${order.total:.2f}")
        
        print("\nItems:")
        for i, (order_item, product) in enumerate(order_items, 1):
            subtotal = order_item.price * order_item.quantity
            print(f"{i}. {product.name}")
            print(f"   Quantity: {order_item.quantity}")
            print(f"   Price: ${order_item.price:.2f}")
            print(f"   Subtotal: ${subtotal:.2f}")
            print()
            
    except Exception as e:
        logger.error(f"Error displaying order: {e}")
        print(f"\n❌ Error retrieving order details: {e}")
    finally:
        session.close()

def list_orders():
    """List all orders in the database."""
    session = Session()
    try:
        orders = session.query(Order).order_by(Order.order_date.desc()).all()
        print(f"\n📦 Found {len(orders)} orders:\n")
        
        for i, order in enumerate(orders, 1):
            # Get customer name
            customer = session.query(Customer).filter(Customer.id == order.customer_id).first()
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
            
            print(f"{i}. Order {order.id}")
            print(f"   Date: {order.order_date.strftime('%Y-%m-%d')}")
            print(f"   Customer: {customer_name}")
            print(f"   Total: ${order.total:.2f}")
            print(f"   Status: {order.status}")
            print()
            
        # Ask if user wants to view a specific order
        print("\nEnter an order number to view details (or press Enter to return):")
        choice = input("> ").strip()
        
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(orders):
                display_order_details(orders[idx].id)
        
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        print(f"\n❌ Error retrieving orders: {e}")
    finally:
        session.close()

def search_customers(term):
    """Search for customers by name or email."""
    session = Session()
    try:
        # Use LIKE for case-insensitive search
        search_pattern = f"%{term}%"
        customers = session.query(Customer).filter(
            (Customer.first_name.like(search_pattern)) | 
            (Customer.last_name.like(search_pattern)) |
            (Customer.email.like(search_pattern))
        ).all()
        
        print(f"\n🔍 Found {len(customers)} customers matching '{term}':\n")
        
        for i, customer in enumerate(customers, 1):
            print(f"{i}. {customer.first_name} {customer.last_name}")
            print(f"   ID: {customer.id}")
            print(f"   Email: {customer.email}")
            print(f"   Loyalty Points: {customer.loyalty_points}")
            print()
            
        # Ask if user wants to view a specific customer
        if customers:
            print("\nEnter a customer number to view details (or press Enter to return):")
            choice = input("> ").strip()
            
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(customers):
                    view_customer_details(customers[idx].id)
        
        return len(customers)
    finally:
        session.close()

def get_customer_stats():
    """Display statistics about customers in the database."""
    session = Session()
    try:
        # Count customers
        total_customers = session.query(Customer).count()
        
        # Count orders
        total_orders = session.query(Order).count()
        
        # Count order items
        total_order_items = session.query(OrderItem).count()
        
        # Calculate average order value
        if total_orders > 0:
            avg_order_value = session.query(Order).with_entities(func.avg(Order.total)).scalar() or 0
        else:
            avg_order_value = 0
        
        # Calculate total revenue
        total_revenue = session.query(Order).with_entities(func.sum(Order.total)).scalar() or 0
        
        # Display stats
        print("\n📊 Customer Database Statistics:")
        print(f"Total Customers: {total_customers}")
        print(f"Total Orders: {total_orders}")
        print(f"Total Order Items: {total_order_items}")
        print(f"Average Order Value: ${avg_order_value:.2f}")
        print(f"Total Revenue: ${total_revenue:.2f}")
        
        # Count orders by status
        print("\nOrders by Status:")
        statuses = session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        for status, count in statuses:
            print(f"  {status}: {count}")
            
    except Exception as e:
        logger.error(f"Error getting customer stats: {e}")
        print(f"\n❌ Error retrieving customer statistics: {e}")
    finally:
        session.close()

def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("👥 BETTERSALE CUSTOMER DATABASE EXPLORER 👥".center(60))
    print("=" * 60)
    print("\nChoose an option:")
    print("1. List all customers")
    print("2. View customer details & order history")
    print("3. List all orders")
    print("4. Search customers")
    print("5. Customer statistics")
    print("6. Exit")
    print("\nEnter your choice (1-6):")

def run_interactive_menu():
    """Run the interactive menu system."""
    while True:
        display_menu()
        choice = input("> ").strip()
        
        if choice == "1":
            list_customers()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            view_customer_details()
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            list_orders()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            print("\nEnter search term (name or email):")
            term = input("> ").strip()
            if term:
                search_customers(term)
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            get_customer_stats()
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            print("\nThank you for using the BetterSale customer database explorer!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

def main():
    """Main function to run the customer database browser."""
    print("\n👥 BetterSale Customer Database Explorer")
    
    # Import the SQL functions only if needed
    try:
        from sqlalchemy import func
    except ImportError:
        logger.error("Error importing sqlalchemy.func")
        return
    
    if not ensure_database():
        logger.error("Failed to initialize database. Exiting.")
        return
    
    run_interactive_menu()

if __name__ == "__main__":
    main()
