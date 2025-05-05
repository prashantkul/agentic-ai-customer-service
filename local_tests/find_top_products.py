#!/usr/bin/env python3
"""
Identify the top products that would be displayed first in the Streamlit app.
"""

import logging
from customer_service.database.models import Session, Product

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    """Find the top products that would be displayed first."""
    session = Session()
    
    try:
        # First identify sample products (the ones added in init_db.py)
        # These are likely to be displayed first
        sample_products = session.query(Product).filter(
            Product.id.in_([
                'TEN-SHOE-01', 'TEN-RAC-ADV', 'TNB-003',
                'RUN-S05', 'RUN-A01', 'RUN-W01',
                'BKB-007', 'BKB-S01', 'BKB-A02',
                'GEN-WB-01'
            ])
        ).all()
        
        if sample_products:
            print("\nTop Products (Sample Products):")
            print("------------------------------")
            
            for i, product in enumerate(sample_products, 1):
                print(f"{i}. {product.name} (ID: {product.id})")
                print(f"   Sport: {product.sport}, Category: {product.category}")
                print(f"   Image Path: {product.image_url}")
                print()
        
        # Also fetch the first 10 products that would be displayed
        # when no filter is applied (default sorting)
        print("\nTop 10 Products (Default Sorting):")
        print("--------------------------------")
        
        top_products = session.query(Product).limit(10).all()
        
        for i, product in enumerate(top_products, 1):
            print(f"{i}. {product.name} (ID: {product.id})")
            print(f"   Sport: {product.sport}, Category: {product.category}")
            print(f"   Image Path: {product.image_url}")
            print()
        
    except Exception as e:
        logger.error(f"Error querying database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()