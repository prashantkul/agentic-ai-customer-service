#!/usr/bin/env python3
"""
Streamlit app for the Customer Service Agent.
A modular implementation with components for different parts of the application.
"""

import uuid
import streamlit as st

# Import components
from streamlit_components.config import logger
from streamlit_components.chat import display_chat_messages, handle_user_input
from streamlit_components.cart import display_cart, display_order_confirmation
from streamlit_components.order import display_action_buttons
from streamlit_components.debug import display_debug_section
from streamlit_components.agent import process_agent_interaction
from streamlit_components.inventory import display_inventory, display_products_by_sport

# --- Page Configuration ---
st.set_page_config(page_title="BetterSale Customer Service", layout="wide")

# --- Header ---
with st.container():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("better-sale-logo.png", width=80)
        except FileNotFoundError:
            st.warning("Logo image not found.")
    with col2:
        st.title("BetterSale Customer Service")
        st.caption("Your one-stop shop for sports equipment")
    st.divider()

# --- Initialize Session State Variables ---
if "messages" not in st.session_state:
    # Force the first message to be a request for account info to trigger the formatted response
    st.session_state.messages = [
        {"role": "user", "content": "Hello, can you show me my account information?"}
    ]
    # This will be replaced by the agent's response with customer info
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.session_initialized = False
if "cart" not in st.session_state:
    st.session_state.cart = []
if "processing_message" not in st.session_state:
    st.session_state.processing_message = False  # Flag to prevent re-entry
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Shop"  # Default tab

# --- Tab Navigation ---
tabs = st.tabs(["Shop with Agent", "Cart"])

# Track which tab is active 
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Shop with Agent"

# Detect tab changes to trigger actions
tab_changed = False
if st.session_state.current_tab != tabs[0].label and tabs[0].label == "Shop with Agent":
    st.session_state.current_tab = "Shop with Agent"
    tab_changed = True
elif st.session_state.current_tab != tabs[1].label and tabs[1].label == "Cart":
    st.session_state.current_tab = "Cart"
    tab_changed = True
    
    # When we switch to Cart tab, request cart refresh
    st.session_state.cart_refresh_requested = True

# --- Shop with Agent Tab ---
with tabs[0]:
    # First row - Cart in top right corner
    _, cart_col = st.columns([4, 1])
    with cart_col:
        with st.container(border=True):
            if not display_order_confirmation(location_suffix="_shop_top"):
                display_cart()
                # Display mini action button
                display_action_buttons(key_suffix="_cart_top")
    
    # Second row - Main content columns
    shop_col, chat_col = st.columns([3, 2])
    
    with shop_col:
        st.header("Product Catalog")
        # Display inventory grid
        display_inventory()
        
        # Display products by sport (expandable sections)
        display_products_by_sport()
    
    with chat_col:
        # Add space to align with first product row
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        # Full container with border for the entire assistant section
        with st.container(border=True):
            st.header("Shopping Assistant")
            
            # Enhanced welcome message with clearer instructions
            with st.container():
                st.markdown("#### Welcome to BetterSale's AI Shopping Assistant!")
                st.markdown("""
                I can help you:
                - Find products that match your needs
                - Add items to your cart
                - Answer questions about our products
                - Provide recommendations based on your preferences
                """)
                st.info("Just tell me what you're looking for or which products you want to add to your cart.")
            
            # Display chat interface in a styled container
            with st.container():
                display_chat_messages()
                handle_user_input()

# --- Cart Tab ---
with tabs[1]:
    # Check if we need to refresh the cart
    if st.session_state.get("cart_refresh_requested", False):
        # Add a message to trigger cart refresh
        st.session_state.messages.append(
            {"role": "user", "content": "Show me what's in my cart using access_cart_information tool"}
        )
        # Reset the flag
        st.session_state.cart_refresh_requested = False
        # Rerun to process the message
        st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Shopping Cart")
        # Show order confirmation if an order was just submitted
        if not display_order_confirmation(location_suffix="_cart_tab_main"):
            # If no order confirmation to show, display the cart in full width
            display_cart()
    
    with col2:
        st.subheader("Order Summary")
        # Display action buttons with unique key suffix
        display_action_buttons(key_suffix="_cart_tab")

# --- Process agent interactions ---
process_agent_interaction()