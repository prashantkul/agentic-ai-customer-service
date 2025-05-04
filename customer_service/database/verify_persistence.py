#!/usr/bin/env python3
"""
Verify database persistence by creating and retrieving a customer record.
This script tests if the database is correctly persisting data between sessions.
"""

import logging
import uuid
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_persistence():
    """Test database persistence by creating and retrieving a customer."""
    
    # Import database models and operations
    from customer_service.database.models import Session, Customer, Base, engine, create_tables
    
    # Generate a unique customer ID for this test
    unique_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Creating test customer with ID: {unique_id}")
    
    # Step 1: Create a new session
    session1 = Session()
    
    try:
        # Step 2: Create a temporary customer record
        new_customer = Customer(
            id=unique_id,
            account_number=f"ACC-{unique_id}",
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone_number="555-1234",
            customer_start_date="2025-04-24",
            loyalty_points=100,
            preferred_store="Test Store"
        )
        
        # Step 3: Add and commit to database
        session1.add(new_customer)
        session1.commit()
        logger.info(f"Customer {unique_id} created and committed to database")
        
    except Exception as e:
        session1.rollback()
        logger.error(f"Error creating customer: {e}")
        return False
    finally:
        # Step 4: Close the session
        session1.close()
        logger.info("First session closed")
    
    # Step 5: Open a new session
    session2 = Session()
    
    try:
        # Step 6: Try to retrieve the customer record
        retrieved_customer = session2.query(Customer).filter(Customer.id == unique_id).first()
        
        # Step 7: Check if customer was found
        if retrieved_customer:
            logger.info(f"SUCCESS: Customer {unique_id} was retrieved from the database")
            logger.info(f"Customer details: {retrieved_customer.first_name} {retrieved_customer.last_name}")
            logger.info(f"Email: {retrieved_customer.email}")
            logger.info(f"Account number: {retrieved_customer.account_number}")
            return True
        else:
            logger.error(f"FAILURE: Customer {unique_id} was NOT found in the database")
            return False
            
    except Exception as e:
        logger.error(f"Error retrieving customer: {e}")
        return False
    finally:
        session2.close()
        logger.info("Second session closed")

if __name__ == "__main__":
    # Make sure tables exist
    try:
        from customer_service.database.models import create_tables
        create_tables()
        logger.info("Database tables exist or were created")
    except Exception as e:
        logger.error(f"Error ensuring database tables exist: {e}")
        sys.exit(1)
    
    # Run the persistence test
    result = verify_persistence()
    
    # Exit with appropriate code
    if result:
        logger.info("PERSISTENCE TEST PASSED: The database is correctly persisting data between sessions.")
        sys.exit(0)
    else:
        logger.error("PERSISTENCE TEST FAILED: The database is not correctly persisting data between sessions.")
        sys.exit(1)