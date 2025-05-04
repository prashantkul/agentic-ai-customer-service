#!/usr/bin/env python3
"""
Script to add 20 new customers with order history to the database.
Products for the orders will be pulled from the existing product table.
"""

import sys
import logging
import random
import uuid
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Import database models
from customer_service.database.models import (
    Session, Customer, Product, Order, OrderItem, CartItem,
    Address, CommunicationPreferences, SportsProfile
)
from customer_service.database.init_db import init_db, ensure_tables_exist

# Sample data for generating customers
FIRST_NAMES = [
    "Emma", "James", "Olivia", "Noah", "Ava", "William", "Sophia", "Benjamin", 
    "Isabella", "Elijah", "Charlotte", "Lucas", "Amelia", "Mason", "Mia", 
    "Alexander", "Harper", "Ethan", "Evelyn", "Daniel", "Abigail", "Matthew"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson"
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com"]

CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
          "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
          "Seattle", "Denver", "Boston", "Portland", "Atlanta", "Miami"]

STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

SPORTS = ["Tennis", "Running", "Basketball", "Soccer", "Golf", "Swimming", "Cycling", "Yoga", "Hiking"]
SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Professional"]
ACTIVITY_FREQUENCY = ["Daily", "Weekly", "Bi-weekly", "Monthly", "Occasionally"]
PHONE_AREA_CODES = ["206", "408", "415", "650", "212", "718", "305", "312", "404", "713", "214"]

STORES = ["BetterSale Sports Center", "BetterSale Downtown", "BetterSale Outlet", "BetterSale Mall"]

def generate_phone_number():
    """Generate a random phone number."""
    area_code = random.choice(PHONE_AREA_CODES)
    prefix = str(random.randint(100, 999))
    line = str(random.randint(1000, 9999))
    return f"+1-{area_code}-{prefix}-{line}"

def generate_address():
    """Generate a random address."""
    street_number = str(random.randint(100, 9999))
    street_names = ["Main St", "Oak Ave", "Maple Rd", "Washington Blvd", "Park Ave", 
                   "Lake St", "River Rd", "Mountain View", "Sunset Blvd", "Broadway"]
    street = f"{street_number} {random.choice(street_names)}"
    city = random.choice(CITIES)
    state = random.choice(list(STATES.keys()))
    zip_code = str(random.randint(10000, 99999))
    
    return {
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code
    }

def generate_sports_profile():
    """Generate a random sports profile."""
    # Pick 1-3 random sports
    num_sports = random.randint(1, 3)
    preferred_sports = random.sample(SPORTS, num_sports)
    
    # Generate skill levels for each preferred sport
    skill_level = {}
    for sport in preferred_sports:
        skill_level[sport] = random.choice(SKILL_LEVELS)
    
    # Pick random favorite teams
    teams = ["Lakers", "Dodgers", "Yankees", "Patriots", "Celtics", "Bulls", "Warriors",
             "Seahawks", "Packers", "Cowboys", "Red Sox", "Chelsea", "Barcelona", "Real Madrid"]
    num_teams = random.randint(0, 3)
    favorite_teams = random.sample(teams, num_teams)
    
    # Pick random interests
    activities = ["Hiking", "Camping", "Fishing", "Biking", "Rock Climbing", "Skiing",
                 "Snowboarding", "Surfing", "Kayaking", "Yoga", "Weight Training", "Dancing"]
    num_interests = random.randint(1, 4)
    interests = random.sample(activities, num_interests)
    
    return {
        "preferred_sports": json.dumps(preferred_sports),
        "skill_level": json.dumps(skill_level),
        "favorite_teams": json.dumps(favorite_teams),
        "interests": json.dumps(interests),
        "activity_frequency": random.choice(ACTIVITY_FREQUENCY)
    }

def generate_customer():
    """Generate a random customer."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
    
    # Generate customer start date (1-5 years ago)
    days_ago = random.randint(365, 365*5)
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
    
    return {
        "id": customer_id,
        "account_number": f"AC{random.randint(100000000, 999999999)}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": generate_phone_number(),
        "customer_start_date": start_date,
        "loyalty_points": random.randint(0, 1000),
        "preferred_store": random.choice(STORES)
    }

def get_random_products(session, count=None, sport=None):
    """
    Get random products from the database.
    
    Args:
        session: SQLAlchemy session
        count: Number of products to return (random if None)
        sport: Filter by sport (optional)
        
    Returns:
        List of Product objects
    """
    query = session.query(Product)
    
    # Filter by sport if specified
    if sport:
        query = query.filter(Product.sport == sport)
    
    # Get all products matching criteria
    products = query.all()
    
    # Return empty list if no products found
    if not products:
        return []
    
    # Determine how many products to return
    if count is None:
        count = random.randint(1, min(5, len(products)))
    else:
        count = min(count, len(products))
    
    # Return random selection of products
    return random.sample(products, count)

def generate_order(session, customer_id, order_date):
    """
    Generate a random order for a customer.
    
    Args:
        session: SQLAlchemy session
        customer_id: Customer ID
        order_date: Date of the order
        
    Returns:
        Tuple of (Order, list of OrderItems)
    """
    # Get 1-5 random products
    products = get_random_products(session, count=random.randint(1, 5))
    
    if not products:
        return None, []
    
    # Create order
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate total
    order_items = []
    total = 0
    
    for product in products:
        quantity = random.randint(1, 3)
        item_price = product.price
        total += item_price * quantity
        
        order_item = OrderItem(
            order_id=order_id,
            product_id=product.id,
            quantity=quantity,
            price=item_price
        )
        order_items.append(order_item)
    
    # Create order with random status
    statuses = ["Completed", "Shipped", "Processing", "Delivered"]
    weights = [0.70, 0.15, 0.10, 0.05]  # More completed orders
    status = random.choices(statuses, weights=weights, k=1)[0]
    
    order = Order(
        id=order_id,
        customer_id=customer_id,
        order_date=order_date,
        total=round(total, 2),
        status=status
    )
    
    return order, order_items

def generate_orders_for_customer(session, customer_id, start_date, count=None):
    """
    Generate random order history for a customer.
    
    Args:
        session: SQLAlchemy session
        customer_id: Customer ID
        start_date: Customer start date
        count: Number of orders (random if None)
        
    Returns:
        List of tuples (Order, list of OrderItems)
    """
    if count is None:
        count = random.randint(0, 5)  # 0-5 orders per customer
    
    orders = []
    
    # Parse start date
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    
    # Generate orders with random dates after customer start date
    for _ in range(count):
        # Random date between start date and now
        days_since_start = (datetime.datetime.now() - start_date_obj).days
        if days_since_start <= 0:
            continue
            
        random_days = random.randint(1, days_since_start)
        order_date = start_date_obj + datetime.timedelta(days=random_days)
        
        # Generate order
        order, order_items = generate_order(session, customer_id, order_date)
        if order:
            orders.append((order, order_items))
    
    return orders

def add_customers_with_history(count=20, clear_existing=False):
    """
    Add specified number of customers with order history to the database.
    
    Args:
        count: Number of customers to add
        clear_existing: If True, clear existing data before adding customers
        
    Returns:
        List of created customer IDs
    """
    logger.info(f"Adding {count} customers with order history...")
    
    # Ensure database tables exist
    if clear_existing:
        init_db(clear_existing=True)
        logger.info("Initialized database and cleared existing data")
    else:
        ensure_tables_exist()
        logger.info("Ensured database tables exist without clearing data")
    
    session = Session()
    customer_ids = []
    
    try:
        for i in range(count):
            # Generate customer data
            customer_data = generate_customer()
            customer_id = customer_data["id"]
            
            # Create customer
            customer = Customer(**customer_data)
            session.add(customer)
            
            # Add address
            address_data = generate_address()
            address = Address(
                customer=customer,
                **address_data
            )
            session.add(address)
            
            # Add communication preferences (random settings)
            comm_prefs = CommunicationPreferences(
                customer=customer,
                email=random.choice([True, False]),
                sms=random.choice([True, False]),
                push_notifications=random.choice([True, False])
            )
            session.add(comm_prefs)
            
            # Add sports profile
            sports_data = generate_sports_profile()
            sports_profile = SportsProfile(
                customer=customer,
                **sports_data
            )
            session.add(sports_profile)
            
            # Add order history
            orders = generate_orders_for_customer(
                session, 
                customer_id, 
                customer_data["customer_start_date"]
            )
            
            for order, order_items in orders:
                session.add(order)
                for item in order_items:
                    session.add(item)
            
            # Maybe add items to current cart (30% chance)
            if random.random() < 0.3:
                # Get 1-3 random products for cart
                cart_products = get_random_products(session, count=random.randint(1, 3))
                
                for product in cart_products:
                    cart_item = CartItem(
                        customer_id=customer_id,
                        product_id=product.id,
                        quantity=random.randint(1, 2),
                        date_added=datetime.datetime.now()
                    )
                    session.add(cart_item)
            
            # Track customer ID
            customer_ids.append(customer_id)
            
            # Log progress
            logger.info(f"Added customer {i+1}/{count}: {customer_data['first_name']} {customer_data['last_name']}")
        
        # Commit the changes
        session.commit()
        logger.info(f"Successfully added {count} customers with order history!")
        
        # Print summary statistics
        orders_count = session.query(Order).count()
        order_items_count = session.query(OrderItem).count()
        cart_items_count = session.query(CartItem).count()
        
        logger.info("\nDatabase Statistics:")
        logger.info(f"Total Customers: {session.query(Customer).count()}")
        logger.info(f"Total Orders: {orders_count}")
        logger.info(f"Total Order Items: {order_items_count}")
        logger.info(f"Total Cart Items: {cart_items_count}")
        
        return customer_ids
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding customers: {e}")
        return []
        
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add customers with order history to the database")
    parser.add_argument("--count", type=int, default=20, help="Number of customers to add")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before adding customers")
    args = parser.parse_args()
    
    # Add customers with order history
    add_customers_with_history(args.count, clear_existing=args.clear)