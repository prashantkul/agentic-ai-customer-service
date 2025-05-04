"""
Inventory display component for the Streamlit app.
Displays products from the database.
"""

import logging
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import database models and operations
try:
    from customer_service.database.models import Session, Product
except ImportError:
    logger.warning("Could not import database models. Using mock data.")
    Session = None
    Product = None

def get_products(sport: Optional[str] = None, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get products from the database, optionally filtered by sport or category.
    
    Args:
        sport: Filter by sport (e.g., "Tennis", "Running")
        category: Filter by category (e.g., "Footwear", "Equipment")
        limit: Maximum number of products to return
        
    Returns:
        List of product dictionaries
    """
    if Session is None:
        # If database not available, return mock data
        return [
            {
                "id": "TEN-SHOE-01",
                "name": "ProCourt Tennis Shoes",
                "description": "Excellent stability for court movement",
                "price": 129.99,
                "category": "Footwear",
                "sport": "Tennis"
            },
            {
                "id": "RUN-S05",
                "name": "CloudRunner Running Shoes",
                "description": "Lightweight and breathable for long distances",
                "price": 139.99,
                "category": "Footwear",
                "sport": "Running"
            }
        ]
    
    # If database is available, query products
    try:
        session = Session()
        query = session.query(Product)
        
        # Apply filters if provided
        if sport:
            query = query.filter(Product.sport == sport)
        if category:
            query = query.filter(Product.category == category)
            
        # Get results
        products = query.limit(limit).all()
        
        # Convert to dictionaries
        result = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "sport": p.sport,
                "image_url": p.image_url
            }
            for p in products
        ]
        
        session.close()
        return result
    except Exception as e:
        logger.error(f"Error fetching products from database: {e}")
        session.close() if 'session' in locals() else None
        # Return empty list on error
        return []

def get_available_sports() -> List[str]:
    """Get unique sports available in the database."""
    if Session is None:
        return ["Tennis", "Running", "Basketball", "Soccer", "Golf"]
        
    try:
        session = Session()
        sports = session.query(Product.sport).distinct().all()
        session.close()
        return [sport[0] for sport in sports if sport[0]]
    except Exception as e:
        logger.error(f"Error fetching sports from database: {e}")
        session.close() if 'session' in locals() else None
        return []

def get_available_categories(sport: Optional[str] = None) -> List[str]:
    """Get unique categories available in the database, optionally filtered by sport."""
    if Session is None:
        return ["Footwear", "Equipment", "Apparel", "Accessories", "Electronics"]
        
    try:
        session = Session()
        query = session.query(Product.category).distinct()
        if sport:
            query = query.filter(Product.sport == sport)
        categories = query.all()
        session.close()
        return [category[0] for category in categories if category[0]]
    except Exception as e:
        logger.error(f"Error fetching categories from database: {e}")
        session.close() if 'session' in locals() else None
        return []

def display_inventory_filters():
    """Display filters for the inventory."""
    # Initialize session state variables if not exists
    if 'inventory_sport' not in st.session_state:
        st.session_state.inventory_sport = None
    if 'inventory_category' not in st.session_state:
        st.session_state.inventory_category = None
        
    # Get available options
    available_sports = get_available_sports()
    
    # Create columns for filters
    col1, col2 = st.columns(2)
    
    # Sport filter
    with col1:
        sport = st.selectbox(
            "Sport", 
            options=["All Sports"] + available_sports,
            key="sport_filter"
        )
        # Update session state
        st.session_state.inventory_sport = None if sport == "All Sports" else sport
        
    # Category filter - depends on selected sport
    with col2:
        available_categories = get_available_categories(st.session_state.inventory_sport)
        category = st.selectbox(
            "Category", 
            options=["All Categories"] + available_categories,
            key="category_filter"
        )
        # Update session state
        st.session_state.inventory_category = None if category == "All Categories" else category

def display_inventory():
    """Display the inventory products in a grid."""
    st.subheader("📦 Product Inventory")

    # Display filters
    display_inventory_filters()

    # Get filtered products
    products = get_products(
        sport=st.session_state.get('inventory_sport'),
        category=st.session_state.get('inventory_category')
    )

    if not products:
        st.info("No products found matching your criteria.")
        return

    # Display products in a grid - 3 columns
    cols = st.columns(3)

    for i, product in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(product["name"])
                st.caption(f"{product['sport']} > {product['category']}")

                # Display image if available
                if product.get("image_url"):
                    try:
                        # The image URL is already in HTTP format
                        image_url = product["image_url"]
                        
                        # Display the image with consistent size
                        st.image(image_url, width=200, output_format="auto")
                        logger.debug(f"Displaying image from: {image_url}")
                    except Exception as e:
                        # If image can't be displayed, show placeholder
                        st.caption(f"Product image: {product['name']}")
                        st.caption(f"Image path: {product['image_url']}")
                        logger.debug(f"Error displaying image: {e}")

                st.write(product["description"])
                st.write(f"**Price:** ${product['price']:.2f}")
                
                # Display product ID and prompt for using agent
                with st.container(border=True):
                    st.caption("**Product ID:** " + product["id"])
                    st.caption("💬 **Ask our Shopping Assistant:**")
                    st.caption(f"\"Add {product['name']} to my cart\"")
                    st.caption(f"\"Tell me more about {product['name']}\"")
                    

    # Display pagination if needed (future enhancement)

def display_products_by_sport():
    """Display products grouped by sport in expandable sections."""
    st.subheader("Products by Sport")
    
    # Get all available sports
    sports = get_available_sports()
    
    # Display products for each sport in expandable sections
    for sport in sports:
        with st.expander(f"{sport} Products"):
            # Get products for this sport
            products = get_products(sport=sport, limit=10)
            
            if not products:
                st.info(f"No {sport} products found.")
                continue
                
            # Display in a table
            df = pd.DataFrame(products)
            # Select columns to display
            if not df.empty:
                display_columns = ["name", "category", "description", "price"]
                display_df = df[display_columns]
                # Rename columns
                display_df = display_df.rename(columns={
                    "name": "Product",
                    "category": "Category",
                    "description": "Description",
                    "price": "Price ($)"
                })
                
                st.dataframe(display_df, hide_index=True)
