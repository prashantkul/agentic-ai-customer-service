"""
Chat interface component for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_chat_messages():
    """Display the chat message history."""
    st.subheader("Conversation")
    # Display existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


def handle_user_input():
    """Process user input and add to message history."""
    if prompt := st.chat_input("Enter your message..."):
        if not st.session_state.processing_message:  # Prevent processing if already running
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()


def is_cart_related_query(prompt):
    """Determine if the query is related to cart or ordering."""
    prompt_lower = prompt.lower()
    return any(
        keyword in prompt_lower
        for keyword in [
            "add",
            "remove",
            "update",
            "cart",
            "checkout",
            "order",
            "buy",
            "purchase",
        ]
    )