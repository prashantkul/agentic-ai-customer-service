#!/usr/bin/env python3
"""
List all product categories by sport for GCS bucket folder structure.
"""

import logging
from customer_service.database.models import Session, Product

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    """List all product categories by sport."""
    session = Session()
    
    try:
        # Get all distinct sports
        sports = session.query(Product.sport).distinct().all()
        sports = sorted([s[0] for s in sports])
        
        print("\nGCS Bucket Folder Structure:")
        print("----------------------------")
        print("gs://bettersale-product-images/")
        
        # For each sport, get all distinct categories
        for sport in sports:
            print(f"├── {sport.lower()}/")
            
            categories = session.query(Product.category).filter(
                Product.sport == sport
            ).distinct().all()
            
            categories = sorted([c[0] for c in categories])
            
            for i, category in enumerate(categories):
                if i == len(categories) - 1:
                    print(f"│   └── {category.lower()}/")
                else:
                    print(f"│   ├── {category.lower()}/")
        
        print("\nFull list of sport/category combinations:")
        print("---------------------------------------")
        
        for sport in sports:
            print(f"\n{sport}:")
            
            categories = session.query(Product.category).filter(
                Product.sport == sport
            ).distinct().all()
            
            categories = sorted([c[0] for c in categories])
            
            for category in categories:
                # Count products in this category
                count = session.query(Product).filter(
                    Product.sport == sport,
                    Product.category == category
                ).count()
                
                print(f"  - {category} ({count} products)")
        
    except Exception as e:
        logger.error(f"Error querying database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()