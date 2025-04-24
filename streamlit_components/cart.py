"""
Cart display and management component for the Streamlit app.
"""

import logging
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

def display_cart():
    """Display the shopping cart in the sidebar."""
    st.subheader("🛒 Your Cart")
    
    # Show if order has been submitted
    if 'order_submitted' in st.session_state and st.session_state.order_submitted:
        st.info("Your cart has been submitted as an order.")
        return
        
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        return
        
    try:
        cart_df = pd.DataFrame(st.session_state.cart)
        if cart_df.empty:
            st.info("Your cart is empty.")
            return
            
        # Adjust columns based on actual keys from access_cart_information tool
        # Common keys might be 'product_name', 'quantity', 'price', 'product_id'
        cols_to_display = [
            col
            for col in [
                "name",
                "product_name",
                "item",
                "quantity",
                "qty",
                "price",
            ]
            if col in cart_df.columns
        ]
        
        if not cols_to_display:  # Fallback if no standard names found
            st.json(st.session_state.cart)
            return
            
        display_df = cart_df[cols_to_display]
        
        # Basic renaming for clarity
        rename_map = {
            "product_name": "Item",
            "name": "Item",
            "item": "Item",
            "quantity": "Qty",
            "qty": "Qty",
            "price": "Price ($)",
        }
        
        display_df = display_df.rename(
            columns={
                k: v
                for k, v in rename_map.items()
                if k in display_df.columns
            }
        )
        
        # Log the dataframe before display for debugging
        logger.info(f"Cart dataframe columns: {display_df.columns.tolist()}")
        logger.info(f"Cart dataframe sample: {display_df.head(1).to_dict('records') if not display_df.empty else 'Empty'}")
        
        st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        # Calculate total
        display_cart_total(cart_df, display_df)
        
    except Exception as e:
        logger.error(f"Error displaying cart DataFrame: {e}")
        st.error("Could not display cart contents.")
        st.json(st.session_state.cart)


def display_cart_total(cart_df, display_df):
    """Calculate and display the cart total."""
    # Get column names
    price_col = next(
        (
            col
            for col in ["price", "Price ($)"]
            if col in display_df.columns
        ),
        None,
    )
    qty_col = next(
        (
            col
            for col in ["quantity", "Qty", "qty"]
            if col in display_df.columns
        ),
        None,
    )

    if price_col and qty_col:
        try:
            # Find the original column names in the cart_df
            orig_price_col = "price" if "price" in cart_df.columns else price_col
            orig_qty_col = "quantity" if "quantity" in cart_df.columns else qty_col
            
            # Calculate subtotal using the original column names
            cart_df["subtotal"] = pd.to_numeric(
                cart_df[orig_price_col], errors="coerce"
            ) * pd.to_numeric(cart_df[orig_qty_col], errors="coerce")
            total = cart_df["subtotal"].sum()
            st.metric("Cart Total", f"${total:.2f}")
        except Exception as calc_e:
            logger.error(f"Error calculating cart total: {calc_e}")
            logger.info(f"Available columns in cart_df: {list(cart_df.columns)}")
            
            # Fallback calculation if we have the subtotal directly
            if "subtotal" in st.session_state.cart[0] if st.session_state.cart else {}:
                # If items have individual subtotals
                try:
                    total = sum(item.get("subtotal", 0) for item in st.session_state.cart)
                    st.metric("Cart Total", f"${total:.2f}")
                except Exception as e:
                    logger.error(f"Error in fallback total calculation: {e}")
            # Another fallback just using the raw data
            elif all(("price" in item and "quantity" in item) for item in st.session_state.cart):
                try:
                    total = sum(item["price"] * item["quantity"] for item in st.session_state.cart)
                    st.metric("Cart Total", f"${total:.2f}")
                except Exception as e:
                    logger.error(f"Error in second fallback calculation: {e}")


def display_order_confirmation():
    """Display order confirmation after submission."""
    if 'order_confirmed' in st.session_state and st.session_state.order_confirmed:
        st.success("✅ Order successfully submitted!")
        
        # Display order details if available
        if 'order_details' in st.session_state:
            with st.expander("Order Details", expanded=True):
                details = st.session_state.order_details
                if isinstance(details, dict):
                    if 'order_id' in details:
                        st.write(f"**Order ID:** {details['order_id']}")
                    if 'order_date' in details:
                        st.write(f"**Order Date:** {details['order_date']}")
                    if 'status' in details:
                        st.write(f"**Status:** {details['status']}")
                    if 'order_total' in details:
                        st.write(f"**Total:** ${details['order_total']:.2f}")
                else:
                    st.json(details)
        
        # Option to start a new order
        if st.button("Start New Order"):
            # Clear the confirmation and reset the cart
            st.session_state.order_confirmed = False
            if 'order_details' in st.session_state:
                del st.session_state.order_details
            st.session_state.cart = []
            st.rerun()
        return True
    return False