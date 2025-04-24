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

# --- Page Configuration ---
st.set_page_config(page_title="Customer Service Chat", layout="wide")

# --- Header ---
with st.container():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("better-sale-logo.png", width=80)
        except FileNotFoundError:
            st.warning("Logo image not found.")
    with col2:
        st.title("Customer Service Chat")
        st.caption("Welcome to BetterSale's Customer Service Chat")
    st.divider()

# --- Initialize Session State Variables ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.session_initialized = False
if "cart" not in st.session_state:
    st.session_state.cart = []
if "processing_message" not in st.session_state:
    st.session_state.processing_message = False  # Flag to prevent re-entry

# --- Main Layout (Chat on Left, Sidebar for Cart/Details) ---
col_chat, col_sidebar = st.columns([3, 1])

# --- Chat Column ---
with col_chat:
    display_chat_messages()
    handle_user_input()

# --- Sidebar Column ---
with col_sidebar:
    # Show order confirmation if an order was just submitted
    if not display_order_confirmation():
        # If no order confirmation to show, display the regular cart
        display_cart()
    
    st.divider()
    
    # Display action buttons (refresh cart, submit order)
    display_action_buttons()
    
    # Debug section
    display_debug_section()

# --- Process agent interactions ---
process_agent_interaction()