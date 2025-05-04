"""
Order management component for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_action_buttons(key_suffix=""):
    """
    Display cart action buttons like refresh and submit.
    
    Args:
        key_suffix: Optional suffix to add to button keys to make them unique
    """
    st.subheader("Actions")
    
    # Only show action buttons if the order hasn't been submitted
    if 'order_confirmed' in st.session_state and st.session_state.order_confirmed:
        return
        
    # Handle different order submission states
    if 'order_submission_state' in st.session_state and st.session_state.order_submission_state == 'confirming':
        display_order_confirmation_dialog(key_suffix)
    else:
        display_standard_buttons(key_suffix)


def display_order_confirmation_dialog(key_suffix=""):
    """
    Display order confirmation dialog to the user.
    
    Args:
        key_suffix: Optional suffix to add to button keys to make them unique
    """
    st.warning("Please confirm your order submission")
    
    # Generate a more unique key using the key_suffix
    # This ensures each instance of the button gets a unique identifier
    location_key = "_sidebar" if not key_suffix else key_suffix
    
    # Use buttons side by side without columns
    cols = st.columns([1, 1])  # Create columns at the top level
    if cols[0].button("Cancel", key=f"cancel_order{location_key}"):
        st.session_state.order_submission_state = None
        st.rerun()
    if cols[1].button("Confirm Order", key=f"confirm_order{location_key}", type="primary"):
        st.session_state.order_submission_state = 'confirmed'
        
        # Create order details for the agent with current cart contents
        order_items = []
        total = 0
        
        if 'cart' in st.session_state and st.session_state.cart:
            for item in st.session_state.cart:
                if all(k in item for k in ['product_id', 'name', 'quantity', 'price']):
                    product_id = item.get('product_id')
                    quantity = item.get('quantity', 1)
                    price = item.get('price', 0)
                    
                    # Add to total
                    try:
                        total += float(price) * int(quantity)
                    except (ValueError, TypeError):
                        pass
                    
                    # Add to order items
                    order_items.append({
                        'product_id': product_id,
                        'quantity': quantity
                    })
        
        # Format a more explicit order submission message with cart details
        items_list = []
        for item in st.session_state.cart:
            if 'name' in item:
                name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 1)
                items_list.append(f"{name} (x{quantity})")
                
        order_message = (
            "I want to finalize and submit my order now with the following items:\n\n"
            f"Items: {', '.join(items_list)}\n"
            f"Total: ${total:.2f}\n\n"
            "Please process this order using the update_salesforce_crm tool and confirm."
        )
            
        # Send the message to the agent
        st.session_state.messages.append(
            {
                "role": "user", 
                "content": order_message
            }
        )
        st.rerun()


def display_standard_buttons(key_suffix=""):
    """
    Display standard cart action buttons.
    
    Args:
        key_suffix: Optional suffix to add to button keys to make them unique
    """
    cols = st.columns([1, 1])  # Create columns at the top level
    if cols[0].button("🔄 Refresh Cart", key=f"refresh_cart_button{key_suffix}", use_container_width=True):
        # Add a more explicit message to trigger cart refresh
        st.session_state.messages.append(
            {"role": "user", "content": "Show me what's in my cart using access_cart_information tool"}
        )
        st.rerun()
    
    if cols[1].button("✅ Submit Order", key=f"submit_order_button{key_suffix}", use_container_width=True):
        if st.session_state.cart:
            # Set the order submission state
            st.session_state.order_submission_state = 'confirming'
            st.rerun()
        else:
            st.warning("Your cart is empty.")