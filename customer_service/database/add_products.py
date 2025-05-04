#!/usr/bin/env python3
"""
Script to add 100 new sports-related products to the database.
"""

import sys
import logging
from pathlib import Path
import json

# Import database models and session
from customer_service.database.models import Session, Product
from customer_service.database.init_db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Google Cloud Storage bucket name for product images
GCS_BUCKET_NAME = "bettersale-product-images"

# Sports categories with their respective product types
SPORTS_CATALOG = {
    "Tennis": [
        {"id_prefix": "TEN-SHOE", "name": "Tennis Shoes", "category": "Footwear", "price_range": (75, 200)},
        {"id_prefix": "TEN-RAC", "name": "Tennis Racket", "category": "Equipment", "price_range": (60, 350)},
        {"id_prefix": "TEN-BALLS", "name": "Tennis Balls", "category": "Equipment", "price_range": (5, 25)},
        {"id_prefix": "TEN-BAG", "name": "Tennis Bag", "category": "Accessories", "price_range": (40, 150)},
        {"id_prefix": "TEN-APP", "name": "Tennis Apparel", "category": "Apparel", "price_range": (25, 100)},
        {"id_prefix": "TEN-STRI", "name": "Racket Strings", "category": "Equipment", "price_range": (15, 50)},
    ],
    "Running": [
        {"id_prefix": "RUN-SHOE", "name": "Running Shoes", "category": "Footwear", "price_range": (80, 220)},
        {"id_prefix": "RUN-SOCK", "name": "Running Socks", "category": "Apparel", "price_range": (10, 30)},
        {"id_prefix": "RUN-SHIRT", "name": "Running Shirt", "category": "Apparel", "price_range": (25, 85)},
        {"id_prefix": "RUN-SHORT", "name": "Running Shorts", "category": "Apparel", "price_range": (25, 70)},
        {"id_prefix": "RUN-WATCH", "name": "Running Watch", "category": "Electronics", "price_range": (100, 500)},
        {"id_prefix": "RUN-BOTTLE", "name": "Water Bottle", "category": "Accessories", "price_range": (15, 45)},
    ],
    "Basketball": [
        {"id_prefix": "BKB-BALL", "name": "Basketball", "category": "Equipment", "price_range": (20, 90)},
        {"id_prefix": "BKB-SHOE", "name": "Basketball Shoes", "category": "Footwear", "price_range": (90, 250)},
        {"id_prefix": "BKB-HOOP", "name": "Basketball Hoop", "category": "Equipment", "price_range": (100, 600)},
        {"id_prefix": "BKB-JERSEY", "name": "Basketball Jersey", "category": "Apparel", "price_range": (35, 120)},
        {"id_prefix": "BKB-SHORT", "name": "Basketball Shorts", "category": "Apparel", "price_range": (30, 90)},
        {"id_prefix": "BKB-SOCK", "name": "Basketball Socks", "category": "Apparel", "price_range": (10, 30)},
    ],
    "Soccer": [
        {"id_prefix": "SOC-BALL", "name": "Soccer Ball", "category": "Equipment", "price_range": (20, 150)},
        {"id_prefix": "SOC-CLEAT", "name": "Soccer Cleats", "category": "Footwear", "price_range": (60, 250)},
        {"id_prefix": "SOC-GOAL", "name": "Soccer Goal", "category": "Equipment", "price_range": (80, 350)},
        {"id_prefix": "SOC-JERSEY", "name": "Soccer Jersey", "category": "Apparel", "price_range": (40, 120)},
        {"id_prefix": "SOC-SHORT", "name": "Soccer Shorts", "category": "Apparel", "price_range": (25, 65)},
        {"id_prefix": "SOC-SOCK", "name": "Soccer Socks", "category": "Apparel", "price_range": (10, 30)},
    ],
    "Golf": [
        {"id_prefix": "GOLF-CLUB", "name": "Golf Club", "category": "Equipment", "price_range": (100, 800)},
        {"id_prefix": "GOLF-BALL", "name": "Golf Balls", "category": "Equipment", "price_range": (15, 60)},
        {"id_prefix": "GOLF-BAG", "name": "Golf Bag", "category": "Equipment", "price_range": (70, 350)},
        {"id_prefix": "GOLF-SHOE", "name": "Golf Shoes", "category": "Footwear", "price_range": (80, 220)},
        {"id_prefix": "GOLF-GLOVE", "name": "Golf Glove", "category": "Accessories", "price_range": (15, 45)},
        {"id_prefix": "GOLF-SHIRT", "name": "Golf Shirt", "category": "Apparel", "price_range": (35, 95)},
    ],
    "Swimming": [
        {"id_prefix": "SWIM-SUIT", "name": "Swimsuit", "category": "Apparel", "price_range": (30, 120)},
        {"id_prefix": "SWIM-GOGGLE", "name": "Swim Goggles", "category": "Equipment", "price_range": (15, 80)},
        {"id_prefix": "SWIM-CAP", "name": "Swim Cap", "category": "Equipment", "price_range": (8, 30)},
        {"id_prefix": "SWIM-TOWEL", "name": "Swim Towel", "category": "Accessories", "price_range": (20, 60)},
        {"id_prefix": "SWIM-BOARD", "name": "Kickboard", "category": "Equipment", "price_range": (15, 40)},
        {"id_prefix": "SWIM-FIN", "name": "Swim Fins", "category": "Equipment", "price_range": (25, 70)},
    ],
    "Cycling": [
        {"id_prefix": "CYCLE-BIKE", "name": "Bicycle", "category": "Equipment", "price_range": (300, 3000)},
        {"id_prefix": "CYCLE-HELM", "name": "Cycling Helmet", "category": "Safety", "price_range": (40, 200)},
        {"id_prefix": "CYCLE-JERSEY", "name": "Cycling Jersey", "category": "Apparel", "price_range": (30, 150)},
        {"id_prefix": "CYCLE-SHORT", "name": "Cycling Shorts", "category": "Apparel", "price_range": (35, 120)},
        {"id_prefix": "CYCLE-LIGHT", "name": "Bike Lights", "category": "Accessories", "price_range": (20, 100)},
        {"id_prefix": "CYCLE-LOCK", "name": "Bike Lock", "category": "Accessories", "price_range": (15, 120)},
    ],
    "Yoga": [
        {"id_prefix": "YOGA-MAT", "name": "Yoga Mat", "category": "Equipment", "price_range": (20, 120)},
        {"id_prefix": "YOGA-BLOCK", "name": "Yoga Block", "category": "Equipment", "price_range": (10, 30)},
        {"id_prefix": "YOGA-STRAP", "name": "Yoga Strap", "category": "Equipment", "price_range": (8, 25)},
        {"id_prefix": "YOGA-PANTS", "name": "Yoga Pants", "category": "Apparel", "price_range": (25, 120)},
        {"id_prefix": "YOGA-TOP", "name": "Yoga Top", "category": "Apparel", "price_range": (20, 80)},
        {"id_prefix": "YOGA-TOWEL", "name": "Yoga Towel", "category": "Accessories", "price_range": (15, 45)},
    ],
    "Hiking": [
        {"id_prefix": "HIKE-BOOT", "name": "Hiking Boots", "category": "Footwear", "price_range": (80, 250)},
        {"id_prefix": "HIKE-PACK", "name": "Backpack", "category": "Equipment", "price_range": (60, 300)},
        {"id_prefix": "HIKE-POLE", "name": "Trekking Poles", "category": "Equipment", "price_range": (30, 150)},
        {"id_prefix": "HIKE-JACKET", "name": "Hiking Jacket", "category": "Apparel", "price_range": (70, 350)},
        {"id_prefix": "HIKE-SOCK", "name": "Hiking Socks", "category": "Apparel", "price_range": (12, 30)},
        {"id_prefix": "HIKE-BOTTLE", "name": "Insulated Bottle", "category": "Accessories", "price_range": (20, 65)},
    ],
}

# Product variations, brands, and features to create diverse products
VARIATIONS = {
    "Tennis": {
        "Brands": ["ProSpin", "AceServe", "PowerCourt", "GrandSlam", "TopSpin"],
        "Features": {
            "Footwear": ["Clay Court", "Hard Court", "All Court", "Indoor Court", "Pro Tour"],
            "Equipment": ["Carbon Fiber", "Graphite", "Aluminum", "Professional", "Beginner"],
            "Apparel": ["Breathable", "Moisture-Wicking", "UV Protection", "Tournament", "Training"],
            "Accessories": ["Premium", "Professional", "Lightweight", "Durable", "Water-Resistant"]
        }
    },
    "Running": {
        "Brands": ["RoadRunner", "SpeedForce", "TrailMax", "UltraStride", "MilesAhead"],
        "Features": {
            "Footwear": ["Trail", "Road", "Marathon", "Cushioned", "Lightweight"],
            "Apparel": ["Reflective", "Compression", "All-Weather", "Thermal", "Lightweight"],
            "Electronics": ["GPS", "Heart Rate Monitor", "Bluetooth", "Training", "Water-Resistant"],
            "Accessories": ["Hydration", "Storage", "Lightweight", "Insulated", "BPA-Free"]
        }
    },
    "Basketball": {
        "Brands": ["CourtKing", "SlamDunk", "HoopStar", "BallPro", "AirGame"],
        "Features": {
            "Footwear": ["High-Top", "Mid-Top", "Low-Top", "Indoor", "Outdoor"],
            "Equipment": ["Indoor", "Outdoor", "Official Size", "Training", "Professional"],
            "Apparel": ["Breathable", "Moisture-Wicking", "Performance", "Reversible", "Streetball"],
            "Accessories": ["Professional", "Training", "Youth", "Adjustable", "Portable"]
        }
    },
    "Soccer": {
        "Brands": ["GoalStrike", "FieldMaster", "KickPro", "WorldCup", "ScorePerfect"],
        "Features": {
            "Footwear": ["Firm Ground", "Soft Ground", "Indoor", "Turf", "Training"],
            "Equipment": ["Match Ball", "Training Ball", "Professional", "Youth", "Futsal"],
            "Apparel": ["Breathable", "Moisture-Wicking", "Club", "Professional", "Replica"],
            "Accessories": ["Professional", "Training", "Tournament", "Practice", "Indoor"]
        }
    },
    "Golf": {
        "Brands": ["GreenMaster", "FairwayPro", "DriveMax", "PuttPerfect", "TeeElite"],
        "Features": {
            "Footwear": ["Waterproof", "Spiked", "Spikeless", "Tour", "Classic"],
            "Equipment": ["Driver", "Iron Set", "Putter", "Wedge", "Hybrid"],
            "Apparel": ["UV Protection", "Moisture-Wicking", "Tournament", "Classic", "Performance"],
            "Accessories": ["Premium", "Tournament", "Practice", "Weather-Resistant", "Ergonomic"]
        }
    },
    "Swimming": {
        "Brands": ["AquaSpeed", "WaveDive", "SwimPro", "TorpedoSwim", "HydroElite"],
        "Features": {
            "Apparel": ["Competition", "Training", "Chlorine-Resistant", "Hydrodynamic", "Open Water"],
            "Equipment": ["Anti-Fog", "UV Protection", "Racing", "Training", "Competitive"],
            "Accessories": ["Quick-Dry", "Microfiber", "Lightweight", "Competition", "Training"]
        }
    },
    "Cycling": {
        "Brands": ["PedalPower", "SpinMax", "VeloElite", "RoadRider", "TrailCruiser"],
        "Features": {
            "Equipment": ["Road", "Mountain", "Hybrid", "Electric", "Urban"],
            "Safety": ["Ventilated", "MIPS Technology", "Aerodynamic", "LED", "Lightweight"],
            "Apparel": ["Padded", "Aerodynamic", "Reflective", "Weather-Resistant", "UV Protection"],
            "Accessories": ["Waterproof", "High-Visibility", "USB Rechargeable", "Anti-Theft", "Lightweight"]
        }
    },
    "Yoga": {
        "Brands": ["ZenFlow", "FlexPose", "OmBalance", "NamasteFit", "AsanaCore"],
        "Features": {
            "Equipment": ["Non-Slip", "Eco-Friendly", "Extra Thick", "Alignment", "Travel"],
            "Apparel": ["4-Way Stretch", "Moisture-Wicking", "Breathable", "Seamless", "Sustainable"],
            "Accessories": ["Extra Long", "Natural", "Premium", "Washable", "Hot Yoga"]
        }
    },
    "Hiking": {
        "Brands": ["TrailBlaze", "SummitSeeker", "PathFinder", "TerrainTrek", "AlpineView"],
        "Features": {
            "Footwear": ["Waterproof", "Vibram Sole", "Gore-Tex", "Lightweight", "Ankle Support"],
            "Equipment": ["Ultralight", "Hydration", "Ventilated", "Water-Resistant", "Adjustable"],
            "Apparel": ["Waterproof", "Breathable", "Insulated", "UV Protection", "Quick-Dry"],
            "Accessories": ["BPA-Free", "Vacuum Insulated", "Leak-Proof", "Double Wall", "Wide Mouth"]
        }
    },
}

# Product descriptions - will be generated based on product type
DESCRIPTION_TEMPLATES = {
    "Tennis": {
        "Footwear": "{brand} {feature} tennis shoes designed for optimal court performance and comfort.",
        "Equipment": "{brand} {feature} tennis racket with perfect balance and precision for players of all levels.",
        "Apparel": "{brand} {feature} tennis apparel for maximum performance and style on the court.",
        "Accessories": "{brand} {feature} tennis accessory designed for serious players."
    },
    "Running": {
        "Footwear": "{brand} {feature} running shoes engineered for optimal performance and comfort on any terrain.",
        "Apparel": "{brand} {feature} running apparel designed to enhance performance and comfort during your run.",
        "Electronics": "{brand} {feature} running watch with advanced metrics to track and improve your performance.",
        "Accessories": "{brand} {feature} running accessory to enhance your training and race day experience."
    },
    # Add similar templates for other sports...
}

# Fill in the description templates for all sports
for sport in SPORTS_CATALOG:
    if sport not in DESCRIPTION_TEMPLATES:
        DESCRIPTION_TEMPLATES[sport] = {}
        for product in SPORTS_CATALOG[sport]:
            category = product["category"]
            if category not in DESCRIPTION_TEMPLATES[sport]:
                DESCRIPTION_TEMPLATES[sport][category] = "{brand} {feature} {name} designed for optimal performance and comfort."

# Generate prices within specified ranges
import random

def generate_price(min_price, max_price):
    """Generate a price within the specified range with appropriate decimals."""
    price = random.uniform(min_price, max_price)
    # Round to .99 or .95 endings
    endings = [0.99, 0.95, 0.50, 0.00]
    price = int(price) + random.choice(endings)
    return round(price, 2)

def generate_product_id(prefix, index):
    """Generate a unique product ID."""
    return f"{prefix}-{index:03d}"

def generate_description(sport, category, brand, feature, name):
    """Generate a product description using templates."""
    if sport in DESCRIPTION_TEMPLATES and category in DESCRIPTION_TEMPLATES[sport]:
        template = DESCRIPTION_TEMPLATES[sport][category]
    else:
        template = "{brand} {feature} {name} designed for optimal performance and comfort."
    
    return template.format(brand=brand, feature=feature, name=name)

def generate_products(count=100):
    """Generate a specified number of products for the database."""
    products = []
    current_count = 0
    
    # Distribute products evenly across sports and categories
    while current_count < count:
        for sport, product_types in SPORTS_CATALOG.items():
            if current_count >= count:
                break
                
            sport_variations = VARIATIONS.get(sport, {})
            brands = sport_variations.get("Brands", ["BetterSale"])
            features_by_category = sport_variations.get("Features", {})
            
            for product_type in product_types:
                if current_count >= count:
                    break
                    
                category = product_type["category"]
                features = features_by_category.get(category, ["Premium"])
                
                # Generate a product
                brand = random.choice(brands)
                feature = random.choice(features)
                base_name = product_type["name"]
                price = generate_price(*product_type["price_range"])
                
                product_id = generate_product_id(product_type["id_prefix"], len(products) + 1)
                product_name = f"{brand} {feature} {base_name}"
                description = generate_description(sport, category, brand, feature, base_name)
                
                # Generate a GCS HTTP URL for the product image
                image_filename = f"{product_id.lower().replace('-', '_')}.jpg"
                product = {
                    "id": product_id,
                    "name": product_name,
                    "description": description,
                    "price": price,
                    "category": category,
                    "sport": sport,
                    "image_url": f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/{sport.lower()}/{category.lower()}/{image_filename}"
                }
                
                products.append(product)
                current_count += 1
    
    return products

def add_products_to_database(products):
    """Add the generated products to the database."""
    session = Session()
    
    try:
        for product_data in products:
            # Check if product ID already exists
            existing = session.query(Product).filter(Product.id == product_data["id"]).first()
            if existing:
                logger.info(f"Product with ID {product_data['id']} already exists, skipping.")
                continue
                
            # Create new product
            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                category=product_data["category"],
                sport=product_data["sport"],
                image_url=product_data["image_url"]
            )
            session.add(product)
            logger.info(f"Added product: {product_data['name']} ({product_data['id']})")
        
        # Commit to database
        session.commit()
        logger.info(f"Successfully added {len(products)} products to the database.")
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding products to database: {e}")
        raise
    
    finally:
        session.close()

def main():
    """Main function to generate and add products."""
    logger.info("Ensuring database tables exist...")
    from customer_service.database.init_db import ensure_tables_exist
    ensure_tables_exist()
    
    logger.info("Generating 100 new sports products...")
    products = generate_products(100)
    
    logger.info(f"Adding {len(products)} products to the database...")
    add_products_to_database(products)
    
    logger.info("Done!")
    
    # Optional: Save products to JSON file for reference
    with open(Path(__file__).parent / "generated_products.json", "w") as f:
        json.dump(products, f, indent=2)
    logger.info("Product data saved to generated_products.json")

if __name__ == "__main__":
    main()