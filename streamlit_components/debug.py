"""
Debug tools for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_debug_section():
    """Display debug tools and information."""
    with st.expander("🛠️ Debug Options"):
        if st.button("🔍 Force Cart Check", key="force_cart_check"):
            # This directly tells the agent to use the access_cart_information tool
            st.session_state.messages.append(
                {"role": "user", "content": "Please run the following tool: access_cart_information(customer_id='123')"}
            )
            st.rerun()
            
        # Add debug info toggle
        if 'show_debug_info' not in st.session_state:
            st.session_state.show_debug_info = False
            
        st.session_state.show_debug_info = st.toggle("Show Debug Info", st.session_state.show_debug_info)
        
        if st.session_state.show_debug_info:
            st.subheader("Response Debug Information")
            
            # Show the raw response
            if 'last_raw_response' in st.session_state:
                st.text_area("Last Raw Response (truncated)", 
                             st.session_state.get('last_raw_response', '')[:5000], 
                             height=200)
                
            # Show extracted tool outputs
            if 'tool_outputs' not in st.session_state:
                st.session_state.tool_outputs = {}
            
            # Display tool outputs directly without nesting expanders
            st.subheader("Tool Outputs History")
            st.json(st.session_state.tool_outputs)