"""
Database models for the BetterSale customer service application.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Get database directory
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "bettersale.db")

# Create database engine - using file-based SQLite
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Address(Base):
    """Customer address information."""
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    
    # Relationship back to customer
    customer = relationship("Customer", back_populates="addresses")

class CommunicationPreferences(Base):
    """Customer communication preferences."""
    __tablename__ = 'communication_preferences'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    email = Column(Boolean, default=True)
    sms = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    # Relationship back to customer
    customer = relationship("Customer", back_populates="communication_preferences")

class SportsProfile(Base):
    """Customer sports profile information."""
    __tablename__ = 'sports_profiles'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    preferred_sports = Column(JSON)  # List of sports
    skill_level = Column(JSON)  # Dict mapping sport to skill level
    favorite_teams = Column(JSON)  # List of teams
    interests = Column(JSON)  # List of interests
    activity_frequency = Column(String)  # e.g., weekly, monthly
    
    # Relationship back to customer
    customer = relationship("Customer", back_populates="sports_profile")

class Customer(Base):
    """Customer information."""
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
    
    # Relationships
    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")
    communication_preferences = relationship("CommunicationPreferences", back_populates="customer", 
                                           cascade="all, delete-orphan", uselist=False)
    sports_profile = relationship("SportsProfile", back_populates="customer", 
                                cascade="all, delete-orphan", uselist=False)
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="customer", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="customer", cascade="all, delete-orphan")

class Product(Base):
    """Product information."""
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    sport = Column(String)
    image_url = Column(String, nullable=True)
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")

class CartItem(Base):
    """Items in a customer's shopping cart."""
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    product_id = Column(String, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    date_added = Column(DateTime, default=datetime.datetime.now)
    
    # Relationships
    customer = relationship("Customer", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    """Customer order information."""
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    order_date = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    total = Column(Float)
    discount_applied = Column(String, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """Items within an order."""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Appointment(Base):
    """Customer service appointments."""
    __tablename__ = 'appointments'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    service_type = Column(String)  # e.g., Tennis Lesson, Bike Tune-up
    date = Column(String)
    time_range = Column(String)
    details = Column(String, nullable=True)
    status = Column(String, default="Scheduled")
    
    # Relationships
    customer = relationship("Customer", back_populates="appointments")

# Create all tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(engine)
    logger.info(f"Database tables created at {DB_PATH}")

# Drop all tables
def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(engine)
    logger.info("Database tables dropped")

# Check if database exists and create if not
if not os.path.exists(DB_PATH):
    logger.info(f"Database file not found. Creating at {DB_PATH}")
    create_tables()