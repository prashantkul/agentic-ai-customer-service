"""
Order management component for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_action_buttons():
    """Display cart action buttons like refresh and submit."""
    st.subheader("Actions")
    
    # Only show action buttons if the order hasn't been submitted
    if 'order_confirmed' in st.session_state and st.session_state.order_confirmed:
        return
        
    # Handle different order submission states
    if 'order_submission_state' in st.session_state and st.session_state.order_submission_state == 'confirming':
        display_order_confirmation_dialog()
    else:
        display_standard_buttons()


def display_order_confirmation_dialog():
    """Display order confirmation dialog to the user."""
    st.warning("Please confirm your order submission")
    
    # Use buttons side by side without columns
    cols = st.columns([1, 1])  # Create columns at the top level
    if cols[0].button("Cancel", key="cancel_order"):
        st.session_state.order_submission_state = None
        st.rerun()
    if cols[1].button("Confirm Order", key="confirm_order", type="primary"):
        st.session_state.order_submission_state = 'confirmed'
        # Send the message to the agent
        st.session_state.messages.append(
            {
                "role": "user", 
                "content": "I want to finalize and submit my order now. Please process it and confirm."
            }
        )
        st.rerun()


def display_standard_buttons():
    """Display standard cart action buttons."""
    cols = st.columns([1, 1])  # Create columns at the top level
    if cols[0].button("🔄 Refresh Cart", key="refresh_cart_button", use_container_width=True):
        # Add a more explicit message to trigger cart refresh
        st.session_state.messages.append(
            {"role": "user", "content": "Show me what's in my cart using access_cart_information tool"}
        )
        st.rerun()
    
    if cols[1].button("✅ Submit Order", key="submit_order_button", use_container_width=True):
        if st.session_state.cart:
            # Set the order submission state
            st.session_state.order_submission_state = 'confirming'
            st.rerun()
        else:
            st.warning("Your cart is empty.")