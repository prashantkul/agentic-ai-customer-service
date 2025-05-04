#!/usr/bin/env python3
"""
Standalone test script to browse and search the customer database.
This script provides a simple command-line interface to explore the customers
without importing any agent code that might reset the database.
"""

import sys
import logging
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Configure SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table, DateTime, Boolean, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import json

# Get database directory and path
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(ROOT_DIR, "customer_service", "database", "bettersale.db")

# Create database engine directly
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)

# Test database access
def check_database():
    """Check database connection and print summary of contents."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at: {DB_PATH}")
        return False
        
    logger.info(f"Database file found: {DB_PATH}")
    
    try:
        session = Session()
        
        # Get table names
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Database tables: {', '.join(tables)}")
        
        # Execute raw queries to avoid importing models
        from sqlalchemy import text
        customer_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        logger.info(f"Total customers: {customer_count}")
        
        # List all customers
        customers = session.execute(text("SELECT id, first_name, last_name, email FROM customers")).fetchall()
        logger.info("\nCustomers in database:")
        for customer in customers:
            logger.info(f"- {customer[0]}: {customer[1]} {customer[2]} ({customer[3]})")
        
        # Get order count
        if "orders" in tables:
            order_count = session.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            logger.info(f"\nTotal orders: {order_count}")
            
            # List some orders
            orders = session.execute(text("SELECT id, customer_id, status, total FROM orders LIMIT 5")).fetchall()
            logger.info("\nRecent orders:")
            for order in orders:
                logger.info(f"- {order[0]}: Customer {order[1]}, Status: {order[2]}, Total: ${order[3]:.2f}")
                
        # Get product count
        if "products" in tables:
            product_count = session.execute(text("SELECT COUNT(*) FROM products")).scalar()
            logger.info(f"\nTotal products: {product_count}")
            
            # List some products
            products = session.execute(text("SELECT id, name, price, sport FROM products LIMIT 5")).fetchall() 
            logger.info("\nSample products:")
            for product in products:
                logger.info(f"- {product[0]}: {product[1]}, Price: ${product[2]:.2f}, Sport: {product[3]}")
        
        session.close()
        return True
    except Exception as e:
        logger.error(f"Error accessing database: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== BetterSale Database Checker ===")
    if check_database():
        logger.info("\nDatabase check successful!")
    else:
        logger.error("\nDatabase check failed!")
        sys.exit(1)