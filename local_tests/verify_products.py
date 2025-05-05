#!/usr/bin/env python3
"""
Script to verify product data including images.
"""

import sys
import logging
import json
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    """Verify product data including image URLs."""
    try:
        from customer_service.database.models import Session, Product, DB_PATH
        import os
        
        # Ensure the database is set up but don't reset it
        from customer_service.database.init_db import ensure_tables_exist
        ensure_tables_exist()
        
        print(f"\nDatabase path: {DB_PATH}")
        if not os.path.exists(DB_PATH):
            print("❌ Database file not found!")
            return
        
        session = Session()
        
        try:
            # Count products
            total_products = session.query(Product).count()
            
            # Count products with image URLs
            products_with_images = session.query(Product).filter(
                Product.image_url.isnot(None)
            ).count()
            
            # Calculate percentage
            if total_products > 0:
                image_percentage = (products_with_images / total_products) * 100
            else:
                image_percentage = 0
            
            # Display product statistics
            print("\n" + "=" * 70)
            print("📦 BETTERSALE PRODUCT INVENTORY 📦".center(70))
            print("=" * 70)
            
            print(f"\nTotal Products: {total_products}")
            print(f"Products with Images: {products_with_images} ({image_percentage:.1f}%)")
            
            # Count products by sport
            print("\nProducts by Sport:")
            sport_counts = session.query(
                Product.sport, 
                func.count(Product.id)
            ).group_by(Product.sport).all()
            
            for sport, count in sorted(sport_counts, key=lambda x: x[1], reverse=True):
                print(f"  {sport}: {count}")
            
            # Count products by category
            print("\nProducts by Category:")
            category_counts = session.query(
                Product.category, 
                func.count(Product.id)
            ).group_by(Product.category).all()
            
            for category, count in sorted(category_counts, key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
            
            # Sample products with image URLs
            print("\nSample Products with Image URLs:")
            sample_products = session.query(Product).filter(
                Product.image_url.isnot(None)
            ).limit(5).all()
            
            # Prepare table data
            table_data = []
            for product in sample_products:
                table_data.append([
                    product.id,
                    product.name[:30] + "..." if len(product.name) > 30 else product.name,
                    product.sport,
                    product.category,
                    product.image_url
                ])
            
            print(tabulate(
                table_data,
                headers=["ID", "Name", "Sport", "Category", "Image URL"],
                tablefmt="grid"
            ))
            
            # Check for image URL patterns
            gcs_pattern = "gs://"
            http_pattern = "http"
            
            gcs_count = session.query(Product).filter(
                Product.image_url.like(f"{gcs_pattern}%")
            ).count()
            
            http_count = session.query(Product).filter(
                Product.image_url.like(f"{http_pattern}%")
            ).count()
            
            print(f"\nImage URL Types:")
            print(f"  Google Cloud Storage URLs (gs://): {gcs_count}")
            print(f"  HTTP URLs: {http_count}")
            
            print("\n✅ Product verification complete!")
            
        except Exception as e:
            logger.error(f"Error querying products: {e}")
        finally:
            session.close()
            
    except ImportError as e:
        logger.error(f"Error importing database modules: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        from sqlalchemy import func  # Import here for the group_by queries
        main()
    except Exception as e:
        logger.error(f"Error running verification: {e}")
        sys.exit(1)