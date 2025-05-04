#!/usr/bin/env python3
"""
Script to update product image URLs to use Google Cloud Storage.
This will convert any local paths (/images/...) to GCS URLs (gs://).
"""

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Google Cloud Storage bucket name for product images
GCS_BUCKET_NAME = "bettersale-product-images"

def update_image_urls():
    """Update all product image URLs to use GCS."""
    try:
        from customer_service.database.models import Session, Product
        
        session = Session()
        try:
            # Get all products with image URLs that need updating
            # (don't start with https://storage.cloud.google.com/)
            products = session.query(Product).filter(
                Product.image_url.isnot(None),
                ~Product.image_url.like("https://storage.cloud.google.com/%")
            ).all()
            
            count = len(products)
            if count == 0:
                logger.info("No products found with non-GCS image URLs.")
                return
                
            logger.info(f"Found {count} products with non-GCS image URLs.")
            
            # Update each product
            for product in products:
                old_url = product.image_url
                
                # Skip if already a GCS HTTP URL
                if old_url.startswith("https://storage.cloud.google.com/"):
                    continue
                    
                # Convert to lowercase and replace dashes with underscores
                image_filename = product.id.lower().replace('-', '_') + ".jpg"
                sport = product.sport.lower()
                category = product.category.lower()
                
                # Set the new GCS HTTP URL
                new_url = f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/{sport}/{category}/{image_filename}"
                product.image_url = new_url
                
                logger.info(f"Updated {product.id} ({product.name}): {old_url} -> {new_url}")
            
            # Commit the changes
            session.commit()
            logger.info(f"Successfully updated {count} product image URLs.")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating image URLs: {e}")
            raise
            
        finally:
            session.close()
            
    except ImportError as e:
        logger.error(f"Failed to import database modules: {e}")
        return False

def main():
    """Main function to update image URLs."""
    logger.info("Updating product image URLs to use Google Cloud Storage...")
    update_image_urls()
    logger.info("Done!")

if __name__ == "__main__":
    main()