#!/usr/bin/env python3
"""
Script to add test customers to the database without importing the agent module.
"""

import sys
import logging
import os
import random
import uuid
import json
import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Get database directory and path
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(ROOT_DIR, "customer_service", "database", "bettersale.db")

# Configure SQLAlchemy directly
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create database engine directly
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define minimal model classes needed for adding customers
class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(String, primary_key=True)
    account_number = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    customer_start_date = Column(String)
    loyalty_points = Column(Integer, default=0)
    preferred_store = Column(String)

class Address(Base):
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

class CommunicationPreferences(Base):
    __tablename__ = 'communication_preferences'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    email = Column(Boolean, default=True)
    sms = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)

class SportsProfile(Base):
    __tablename__ = 'sports_profiles'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    preferred_sports = Column(JSON)  # List of sports
    skill_level = Column(JSON)  # Dict mapping sport to skill level
    favorite_teams = Column(JSON)  # List of teams
    interests = Column(JSON)  # List of interests
    activity_frequency = Column(String)  # e.g., weekly, monthly

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    sport = Column(String)
    image_url = Column(String, nullable=True)

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    product_id = Column(String, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    date_added = Column(DateTime, default=datetime.datetime.now)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    order_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    total = Column(Float)
    discount_applied = Column(String, nullable=True)

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)

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
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "MI", "GA", "NC"]
SPORTS = ["Tennis", "Running", "Basketball", "Soccer", "Golf", "Swimming", "Cycling", "Yoga", "Hiking"]
SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Professional"]
ACTIVITY_FREQUENCY = ["Daily", "Weekly", "Bi-weekly", "Monthly", "Occasionally"]
STORES = ["BetterSale Sports Center", "BetterSale Downtown", "BetterSale Outlet", "BetterSale Mall"]

def ensure_tables_exist():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
    logger.info("Ensured all database tables exist")

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
        "phone_number": f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "customer_start_date": start_date,
        "loyalty_points": random.randint(0, 1000),
        "preferred_store": random.choice(STORES)
    }

def generate_address():
    """Generate a random address."""
    street_number = str(random.randint(100, 9999))
    street_names = ["Main St", "Oak Ave", "Maple Rd", "Washington Blvd", "Park Ave"]
    street = f"{street_number} {random.choice(street_names)}"
    city = random.choice(CITIES)
    state = random.choice(STATES)
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
    teams = ["Lakers", "Dodgers", "Yankees", "Patriots", "Celtics", "Bulls", "Warriors"]
    num_teams = random.randint(0, 3)
    favorite_teams = random.sample(teams, num_teams)
    
    # Pick random interests
    activities = ["Hiking", "Camping", "Fishing", "Biking", "Rock Climbing", "Skiing", "Yoga"]
    num_interests = random.randint(1, 4)
    interests = random.sample(activities, num_interests)
    
    return {
        "preferred_sports": json.dumps(preferred_sports),
        "skill_level": json.dumps(skill_level),
        "favorite_teams": json.dumps(favorite_teams),
        "interests": json.dumps(interests),
        "activity_frequency": random.choice(ACTIVITY_FREQUENCY)
    }

def add_customers(count=5):
    """Add random customers to the database."""
    logger.info(f"Adding {count} customers to the database...")
    
    session = Session()
    added_customers = []
    
    try:
        # Get current customer count
        current_count = session.query(Customer).count()
        logger.info(f"Current customer count: {current_count}")
        
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
                customer_id=customer_id,
                **address_data
            )
            session.add(address)
            
            # Add communication preferences
            comm_prefs = CommunicationPreferences(
                customer_id=customer_id,
                email=random.choice([True, False]),
                sms=random.choice([True, False]),
                push_notifications=random.choice([True, False])
            )
            session.add(comm_prefs)
            
            # Add sports profile
            sports_data = generate_sports_profile()
            sports_profile = SportsProfile(
                customer_id=customer_id,
                **sports_data
            )
            session.add(sports_profile)
            
            # Add to our list
            added_customers.append(customer_data)
            
            # Log progress
            logger.info(f"Added customer {i+1}/{count}: {customer_data['first_name']} {customer_data['last_name']}")
        
        # Commit changes
        session.commit()
        logger.info(f"Successfully added {count} customers!")
        
        # Get new count
        new_count = session.query(Customer).count()
        logger.info(f"New customer count: {new_count}")
        
        return added_customers
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding customers: {e}")
        return []
    
    finally:
        session.close()

def main():
    """Main function."""
    try:
        # Ensure database tables exist
        ensure_tables_exist()
        
        # Add customers
        add_customers(count=10)
        
        logger.info("Test data added successfully!")
        return True
    except Exception as e:
        logger.error(f"Error adding test data: {e}")
        return False

if __name__ == "__main__":
    main()