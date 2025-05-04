#!/usr/bin/env python3
"""
Test script to browse and search the expanded product database.
This script provides a simple command-line interface to explore the products
without needing to run the ADK agent.
"""

import sys
import logging
from pathlib import Path
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from customer_service.database.models import Session, Product, Customer, Order, OrderItem, create_tables
    from customer_service.database.init_db import init_db
    from customer_service.database.operations import (
        get_product_recommendations,
        access_cart_information,
        modify_cart,
        get_customer_information,
        get_inventory_status,
        get_order_history,
        get_order_by_id,
    )
except ImportError as e:
    logger.error(f"Error importing database modules: {e}")
    logger.error("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def ensure_database():
    """Ensure the database exists and has data."""
    try:
        # Initialize the database if needed
        #init_db()
        logger.info("Database initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def list_products_by_sport(sport):
    """List products for a specific sport."""
    session = Session()
    try:
        products = session.query(Product).filter(Product.sport == sport).all()
        print(f"\n🏆 Found {len(products)} products for {sport}:\n")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} (${product.price:.2f})")
            print(f"   ID: {product.id}")
            print(f"   Category: {product.category}")
            print(f"   Description: {product.description}")
            print()
            
        return len(products)
    finally:
        session.close()

def list_products_by_category(category):
    """List products for a specific category."""
    session = Session()
    try:
        products = session.query(Product).filter(Product.category == category).all()
        print(f"\n🏷️ Found {len(products)} products in category '{category}':\n")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} (${product.price:.2f})")
            print(f"   ID: {product.id}")
            print(f"   Sport: {product.sport}")
            print(f"   Description: {product.description}")
            print()
            
        return len(products)
    finally:
        session.close()

def search_products(term):
    """Search for products containing the search term in name or description."""
    session = Session()
    try:
        # Use LIKE for case-insensitive search
        search_pattern = f"%{term}%"
        products = session.query(Product).filter(
            (Product.name.like(search_pattern)) | 
            (Product.description.like(search_pattern))
        ).all()
        
        print(f"\n🔍 Found {len(products)} products matching '{term}':\n")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} (${product.price:.2f})")
            print(f"   ID: {product.id}")
            print(f"   Sport: {product.sport}")
            print(f"   Category: {product.category}")
            print(f"   Description: {product.description}")
            print()
            
        return len(products)
    finally:
        session.close()

def count_products_by_sport():
    """Count products for each sport."""
    session = Session()
    try:
        # Get unique sports
        sports = session.query(Product.sport).distinct().all()
        sports = [sport[0] for sport in sports]
        
        print("\n📊 Product counts by sport:")
        for sport in sorted(sports):
            count = session.query(Product).filter(Product.sport == sport).count()
            print(f"  {sport}: {count} products")
            
        # Print total
        total = session.query(Product).count()
        print(f"\nTotal products: {total}")
    finally:
        session.close()

def count_products_by_category():
    """Count products for each category."""
    session = Session()
    try:
        # Get unique categories
        categories = session.query(Product.category).distinct().all()
        categories = [category[0] for category in categories]
        
        print("\n📊 Product counts by category:")
        for category in sorted(categories):
            count = session.query(Product).filter(Product.category == category).count()
            print(f"  {category}: {count} products")
    finally:
        session.close()

def view_cart():
    """View the contents of the cart for customer ID 123."""
    try:
        cart_data = access_cart_information("123")
        cart_items = cart_data.get("cart", [])
        subtotal = cart_data.get("subtotal", 0)
        
        if not cart_items:
            print("\n🛒 Cart is empty")
            return
        
        print("\n🛒 Current cart contents:")
        for i, item in enumerate(cart_items, 1):
            name = item.get("name", "Unknown")
            price = item.get("price", 0)
            quantity = item.get("quantity", 1)
            total = price * quantity
            
            print(f"{i}. {name}")
            print(f"   Quantity: {quantity}")
            print(f"   Price: ${price:.2f}")
            print(f"   Total: ${total:.2f}")
            print()
            
        print(f"Subtotal: ${subtotal:.2f}")
    except Exception as e:
        logger.error(f"Error accessing cart: {e}")
        print("\n❌ Error accessing cart information")

def add_to_cart():
    """Add a product to the cart."""
    session = Session()
    
    try:
        # Show available sports
        sports = [sport[0] for sport in session.query(Product.sport).distinct().all()]
        print("\nAvailable sports:")
        for i, sport in enumerate(sports, 1):
            print(f"{i}. {sport}")
            
        print("\nSelect a sport (enter number):")
        try:
            choice = int(input("> ")) - 1
            if choice < 0 or choice >= len(sports):
                print("Invalid choice")
                return
            selected_sport = sports[choice]
        except ValueError:
            print("Please enter a number")
            return
            
        # Show products for selected sport
        products = session.query(Product).filter(Product.sport == selected_sport).all()
        print(f"\nProducts for {selected_sport}:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} (${product.price:.2f}) - {product.id}")
            
        print("\nSelect a product to add (enter number):")
        try:
            choice = int(input("> ")) - 1
            if choice < 0 or choice >= len(products):
                print("Invalid choice")
                return
            selected_product = products[choice]
        except ValueError:
            print("Please enter a number")
            return
            
        # Ask for quantity
        print("\nEnter quantity:")
        try:
            quantity = int(input("> "))
            if quantity <= 0:
                print("Quantity must be positive")
                return
        except ValueError:
            print("Please enter a number")
            return
            
        # Add to cart
        result = modify_cart(
            "123",
            [{"product_id": selected_product.id, "quantity": quantity}],
            []
        )
        
        if result.get("status") == "success":
            print(f"\n✅ Added {quantity} {selected_product.name} to cart")
        else:
            print(f"\n❌ Failed to add to cart: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        print("\n❌ Error adding to cart")
    finally:
        session.close()

def get_recommendations():
    """Get product recommendations for a sport."""
    print("\nEnter a sport to get recommendations:")
    sport = input("> ")
    
    if not sport:
        print("No sport entered")
        return
        
    try:
        recommendations = get_product_recommendations(sport, "123")
        items = recommendations.get("recommendations", [])
        
        if not items:
            print(f"\nNo recommendations found for {sport}")
            return
            
        print(f"\n💡 Recommendations for {sport}:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.get('name')} (${item.get('price', 0):.2f})")
            print(f"   {item.get('description', '')}")
            print()
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        print("\n❌ Error getting recommendations")

def query_inventory_status():
    """Query inventory status for specific products."""
    session = Session()
    try:
        # Show available sports
        sports = [sport[0] for sport in session.query(Product.sport).distinct().all()]
        sport = get_choice_from_list(sports, "Select a sport to view inventory:")
        if not sport:
            return
            
        # Show products for that sport
        products = session.query(Product).filter(Product.sport == sport).all()
        print(f"\nProducts for {sport}:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} (${product.price:.2f}) - {product.id}")
            
        print("\nSelect a product to check inventory (enter number):")
        try:
            choice = int(input("> ")) - 1
            if choice < 0 or choice >= len(products):
                print("Invalid choice")
                return
            selected_product = products[choice]
        except ValueError:
            print("Please enter a number")
            return
            
        # Query inventory status
        try:
            inventory = get_inventory_status(selected_product.id)
            print(f"\n📦 Inventory status for {selected_product.name} (ID: {selected_product.id}):")
            print(f"  Available: {inventory.get('available', False)}")
            print(f"  Quantity in stock: {inventory.get('quantity', 0)}")
            print(f"  Location: {inventory.get('location', 'Main Warehouse')}")
            if 'last_restock' in inventory:
                print(f"  Last restocked: {inventory.get('last_restock')}")
            if 'next_shipment' in inventory:
                print(f"  Next shipment expected: {inventory.get('next_shipment')}")
        except Exception as e:
            logger.error(f"Error getting inventory status: {e}")
            print("\n❌ Error retrieving inventory status")
            
    finally:
        session.close()

def view_customer_information():
    """View detailed customer information."""
    print("\nEnter customer ID (default: 123):")
    customer_id = input("> ").strip() or "123"
    
    try:
        customer_info = get_customer_information(customer_id)
        
        print(f"\n👤 Customer Information (ID: {customer_id}):")
        print(f"  Name: {customer_info.get('name', 'Unknown')}")
        print(f"  Email: {customer_info.get('email', 'Unknown')}")
        print(f"  Phone: {customer_info.get('phone', 'Unknown')}")
        print(f"  Membership: {customer_info.get('membership_level', 'Standard')}")
        
        # Show address if available
        if 'address' in customer_info:
            address = customer_info['address']
            if isinstance(address, dict):
                print("\n📍 Address:")
                print(f"  {address.get('street', '')}")
                print(f"  {address.get('city', '')}, {address.get('state', '')} {address.get('zip', '')}")
                print(f"  {address.get('country', '')}")
        
        # Show preferences if available
        if 'preferences' in customer_info:
            preferences = customer_info['preferences']
            if isinstance(preferences, dict):
                print("\n🏆 Preferences:")
                print(f"  Favorite sports: {', '.join(preferences.get('favorite_sports', []))}")
                print(f"  Communication preference: {preferences.get('communication_preference', 'Email')}")
        
        # Show loyalty info if available
        if 'loyalty' in customer_info:
            loyalty = customer_info['loyalty']
            if isinstance(loyalty, dict):
                print("\n🎖️ Loyalty Program:")
                print(f"  Points: {loyalty.get('points', 0)}")
                print(f"  Member since: {loyalty.get('member_since', 'Unknown')}")
                print(f"  Tier: {loyalty.get('tier', 'Standard')}")
    
    except Exception as e:
        logger.error(f"Error retrieving customer information: {e}")
        print("\n❌ Error retrieving customer information")

def view_order_history():
    """View a customer's order history."""
    print("\nEnter customer ID (default: 123):")
    customer_id = input("> ").strip() or "123"
    
    try:
        orders = get_order_history(customer_id)
        
        if not orders:
            print(f"\nNo order history found for customer {customer_id}")
            return
            
        print(f"\n📜 Order History for Customer {customer_id}:")
        for i, order in enumerate(orders, 1):
            order_id = order.get('order_id', 'Unknown')
            date = order.get('date', 'Unknown')
            status = order.get('status', 'Unknown')
            total = order.get('total', 0)
            
            print(f"\nOrder #{i}: {order_id}")
            print(f"  Date: {date}")
            print(f"  Status: {status}")
            print(f"  Total: ${total:.2f}")
            
            # Show items if available
            if 'items' in order and order['items']:
                print("  Items:")
                for j, item in enumerate(order['items'], 1):
                    name = item.get('name', item.get('product_id', 'Unknown'))
                    quantity = item.get('quantity', 1)
                    price = item.get('price', 0)
                    print(f"    {j}. {name} (x{quantity}) - ${price:.2f}")
    
    except Exception as e:
        logger.error(f"Error retrieving order history: {e}")
        print("\n❌ Error retrieving order history")

def search_order_by_id():
    """Search for an order by its order ID."""
    print("\nEnter Order ID (format: ORD-XXXXX):")
    order_id = input("> ").strip()
    
    if not order_id:
        print("No order ID entered")
        return
    
    try:
        # Get detailed order information
        order_details = get_order_by_id(order_id)
        
        if 'error' in order_details:
            print(f"\n❌ {order_details['error']}")
            return
            
        # Display comprehensive order details
        print(f"\n📦 Order Details for {order_id}")
        print(f"  Date: {order_details.get('date', 'Unknown')}")
        print(f"  Customer: {order_details.get('customer_name', 'Unknown')} (ID: {order_details.get('customer_id', 'Unknown')})")
        print(f"  Status: {order_details.get('status', 'Unknown')}")
        print(f"  Total: ${order_details.get('total', 0):.2f}")
        print(f"  Item Count: {order_details.get('item_count', 0)}")
        
        # Display shipping information if available
        if 'shipping' in order_details:
            shipping = order_details['shipping']
            print("\n📬 Shipping Information:")
            print(f"  Status: {shipping.get('status', 'Unknown')}")
            
            if shipping.get('tracking_number'):
                print(f"  Tracking Number: {shipping.get('tracking_number')}")
                
            if shipping.get('estimated_delivery'):
                print(f"  Estimated Delivery: {shipping.get('estimated_delivery')}")
        
        # Display line items
        if 'items' in order_details and order_details['items']:
            print("\n📝 Order Items:")
            for i, item in enumerate(order_details['items'], 1):
                name = item.get('name', item.get('product_id', 'Unknown'))
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                subtotal = item.get('subtotal', price * quantity)
                
                print(f"  {i}. {name}")
                print(f"     Qty: {quantity}  |  Price: ${price:.2f}  |  Subtotal: ${subtotal:.2f}")
        
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        print(f"\n❌ Error retrieving order information: {e}")

def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("🏪 BETTERSALE SPORTS PRODUCT DATABASE EXPLORER 🏪".center(60))
    print("=" * 60)
    print("\nChoose an option:")
    print("1. List products by sport")
    print("2. List products by category")
    print("3. Search products")
    print("4. View product statistics")
    print("5. View cart")
    print("6. Add product to cart")
    print("7. Get product recommendations")
    print("8. Query inventory status")
    print("9. View customer information")
    print("10. View order history")
    print("11. Search order by ID")
    print("12. Exit")
    print("\nEnter your choice (1-12):")

def get_choice_from_list(options, prompt):
    """Get a choice from a list of options."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
        
    print(f"\n{prompt}")
    try:
        choice = int(input("> ")) - 1
        if choice < 0 or choice >= len(options):
            print("Invalid choice")
            return None
        return options[choice]
    except ValueError:
        print("Please enter a number")
        return None

def run_interactive_menu():
    """Run the interactive menu system."""
    while True:
        display_menu()
        choice = input("> ").strip()
        
        if choice == "1":
            session = Session()
            sports = sorted([sport[0] for sport in session.query(Product.sport).distinct().all()])
            session.close()
            
            sport = get_choice_from_list(sports, "Select a sport:")
            if sport:
                list_products_by_sport(sport)
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            session = Session()
            categories = sorted([cat[0] for cat in session.query(Product.category).distinct().all()])
            session.close()
            
            category = get_choice_from_list(categories, "Select a category:")
            if category:
                list_products_by_category(category)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            print("\nEnter search term:")
            term = input("> ").strip()
            if term:
                search_products(term)
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            count_products_by_sport()
            count_products_by_category()
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            view_cart()
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            add_to_cart()
            input("\nPress Enter to continue...")
            
        elif choice == "7":
            get_recommendations()
            input("\nPress Enter to continue...")
            
        elif choice == "8":
            query_inventory_status()
            input("\nPress Enter to continue...")
            
        elif choice == "9":
            view_customer_information()
            input("\nPress Enter to continue...")
            
        elif choice == "10":
            view_order_history()
            input("\nPress Enter to continue...")
            
        elif choice == "11":
            search_order_by_id()
            input("\nPress Enter to continue...")
            
        elif choice == "12":
            print("\nThank you for using the BetterSale Sports product database explorer!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

def main():
    """Main function to run the product database browser."""
    print("\n🏪 BetterSale Sports Product Database Explorer")
    
    if not ensure_database():
        logger.error("Failed to initialize database. Exiting.")
        return
    
    run_interactive_menu()

if __name__ == "__main__":
    main()
