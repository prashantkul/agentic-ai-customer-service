"""
Initialize the database with sample data.
"""

import logging
import datetime
import json
import sys
from customer_service.database.models import Session, Base, engine
from customer_service.database.models import (
    Customer, Product, CartItem, Order, OrderItem, 
    Address, CommunicationPreferences, SportsProfile, Appointment
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_tables_exist():
    """Ensure database tables exist without clearing existing data."""
    logger.info("Ensuring database tables exist...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    return True

def init_db(clear_existing=False):
    """Initialize the database with sample data."""
    logger.info("Initializing database with sample data...")
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    session = Session()
    
    try:
        # Clear existing data if requested
        if clear_existing:
            logger.info("Clearing existing data...")
            session.query(OrderItem).delete()
            session.query(Order).delete()
            session.query(CartItem).delete()
            session.query(Appointment).delete()
            session.query(Product).delete()
            session.query(SportsProfile).delete()
            session.query(CommunicationPreferences).delete()
            session.query(Address).delete()
            session.query(Customer).delete()
            
            # Create sample customer - only if we're clearing existing data
            alex = Customer(
                id="123",
                account_number="428765091",
                first_name="Alex",
                last_name="Johnson",
                email="alex.johnson@example.com",
                phone_number="+1-702-555-1212",
                customer_start_date="2022-06-10",
                loyalty_points=133,
                preferred_store="BetterSale Sports Center"
            )
            
            # Add address
            alex_address = Address(
                customer=alex,
                street="123 Main St",
                city="Anytown",
                state="CA",
                zip="12345"
            )
            
            # Add communication preferences
            alex_comm_prefs = CommunicationPreferences(
                customer=alex,
                email=True,
                sms=False,
                push_notifications=True
            )
            
            # Add sports profile
            alex_sports = SportsProfile(
                customer=alex,
                preferred_sports=json.dumps(["Tennis", "Running"]),
                skill_level=json.dumps({"Tennis": "Intermediate", "Running": "Beginner"}),
                favorite_teams=json.dumps(["Lakers", "Dodgers"]),
                interests=json.dumps(["Hiking", "Yoga"]),
                activity_frequency="weekly"
            )
            
            session.add_all([alex, alex_address, alex_comm_prefs, alex_sports])
        
        # Add products only if clearing existing data or if we have no products
        product_count = session.query(Product).count()
        if clear_existing or product_count == 0:
            # Only add products if there aren't any or we're resetting
            if product_count > 0:
                logger.info(f"Found {product_count} existing products - skipping product creation")
            else:
                # Google Cloud Storage bucket name for product images
                GCS_BUCKET_NAME = "bettersale-product-images"
                logger.info("No products found - adding sample products with GCS HTTP image URLs")
                products = [
                    # Tennis products
                    Product(
                        id="TEN-SHOE-01",
                        name="ProCourt Tennis Shoes",
                        description="Excellent stability for court movement",
                        price=129.99,
                        category="Footwear",
                        sport="Tennis",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/tennis/footwear/ten_shoe_01.jpg"
                    ),
                    Product(
                        id="TEN-RAC-ADV",
                        name="Advanced Graphite Racket",
                        description="Great for intermediate players seeking more power",
                        price=149.99,
                        category="Equipment",
                        sport="Tennis",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/tennis/equipment/ten_rac_adv.jpg"
                    ),
                    Product(
                        id="TNB-003",
                        name="Tennis Balls (3-pack)",
                        description="Durable, high-performance tennis balls",
                        price=5.99,
                        category="Accessories",
                        sport="Tennis",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/tennis/accessories/tnb_003.jpg"
                    ),
                    
                    # Running products
                    Product(
                        id="RUN-S05",
                        name="CloudRunner Running Shoes",
                        description="Lightweight and breathable for long distances",
                        price=139.99,
                        category="Footwear",
                        sport="Running",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/running/footwear/run_s05.jpg"
                    ),
                    Product(
                        id="RUN-A01",
                        name="Running Socks (3-pack)",
                        description="Moisture-wicking and blister protection",
                        price=15.76,
                        category="Accessories",
                        sport="Running",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/running/accessories/run_a01.jpg"
                    ),
                    Product(
                        id="RUN-W01",
                        name="GPS Running Watch",
                        description="Track your pace, distance, and heart rate",
                        price=199.99,
                        category="Electronics",
                        sport="Running",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/running/electronics/run_w01.jpg"
                    ),
                    
                    # Basketball products
                    Product(
                        id="BKB-007",
                        name="Official Size Basketball",
                        description="Durable composite leather for indoor/outdoor play",
                        price=29.99,
                        category="Equipment",
                        sport="Basketball",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/basketball/equipment/bkb_007.jpg"
                    ),
                    Product(
                        id="BKB-S01",
                        name="High-Top Basketball Shoes",
                        description="Superior ankle support and cushioning",
                        price=119.99,
                        category="Footwear",
                        sport="Basketball",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/basketball/footwear/bkb_s01.jpg"
                    ),
                    Product(
                        id="BKB-A02",
                        name="Basketball Hoop (Portable)",
                        description="Adjustable height, easy to move",
                        price=249.99,
                        category="Equipment",
                        sport="Basketball",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/basketball/equipment/bkb_a02.jpg"
                    ),
                    
                    # General products
                    Product(
                        id="GEN-WB-01",
                        name="Insulated Water Bottle",
                        description="Keeps drinks cold during any activity",
                        price=19.99,
                        category="Accessories",
                        sport="General",
                        image_url=f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/general/accessories/gen_wb_01.jpg"
                    )
                ]
                
                session.add_all(products)
        
        # Only add cart items for Alex if clearing existing data
        if clear_existing:
            # Add initial cart items for Alex
            alex_cart_items = [
                CartItem(
                    customer=alex,
                    product_id="RUN-S05",  # CloudRunner Running Shoes
                    quantity=1
                ),
                CartItem(
                    customer=alex,
                    product_id="RUN-A01",  # Running Socks
                    quantity=1
                )
            ]
            
            session.add_all(alex_cart_items)
            
            # Create a previous order for Alex
            past_order = Order(
                id="ORD-12345678",
                customer=alex,
                order_date=datetime.datetime.now() - datetime.timedelta(days=30),
                status="Completed",
                total=85.98
            )
            
            order_items = [
                OrderItem(
                    order=past_order,
                    product_id="TNR-001",  # Tennis Racket (dummy product)
                    quantity=1,
                    price=59.99
                ),
                OrderItem(
                    order=past_order,
                    product_id="TNB-003",  # Tennis Balls
                    quantity=2,
                    price=5.99
                )
            ]
            
            session.add(past_order)
            session.add_all(order_items)
            
        # Add 50 additional customers with order history if requested
        if clear_existing:
            logger.info("Skipping additional customer creation since clear_existing=True")
            logger.info("To add customers, run add_customers.py script separately")
        else:
            # Import the add_customers function from the add_customers module
            from customer_service.database.add_customers import add_customers_with_history
            
            # Check current customer count
            customer_count = session.query(Customer).count()
            if customer_count < 10:  # Only add more if we have fewer than 10
                logger.info(f"Found {customer_count} customers - adding more customers with history")
                
                # We'll add customers in this transaction, but let's commit first
                session.commit()
                
                # Close this session
                session.close()
                
                # Add 50 customers with order history
                add_customers_with_history(count=50, clear_existing=False)
                
                # Start a new session for remaining work
                session = Session()
            else:
                logger.info(f"Found {customer_count} customers - skipping additional customer creation")
        
        # Commit changes
        session.commit()
        logger.info("Database initialized with sample data")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    
    finally:
        session.close()

if __name__ == "__main__":
    init_db()