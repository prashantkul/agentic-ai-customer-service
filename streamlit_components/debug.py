"""
Debug tools for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_debug_section():
    """Display debug tools and information in a more compact format."""
    with st.expander("🔧 Developer Tools", expanded=True):
        # Single button for cart refresh
        if st.button("🔍 Refresh Cart", key="force_cart_check", use_container_width=True):
            # This directly tells the agent to use the access_cart_information tool
            st.session_state.messages.append(
                {"role": "user", "content": "Please run the following tool: access_cart_information(customer_id='CUST-80CA281C')"}
            )
            st.rerun()

        # Force display of customer info
        if st.button("👤 Show Customer Info", key="force_customer_info", use_container_width=True):
            st.session_state.messages.append(
                {"role": "user", "content": "Please show me my account information."}
            )
            st.rerun()
            
        # Button to inspect session state
        if st.button("🔍 Inspect Session State", key="inspect_session", use_container_width=True):
            st.session_state.show_session_debug = True
            st.rerun()
            
        # Clear chat history
        if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat history has been cleared. How can I help you today?"}
            ]
            st.rerun()
        
        # Add debug info toggle
        if 'show_debug_info' not in st.session_state:
            st.session_state.show_debug_info = True
            
        st.session_state.show_debug_info = st.toggle("Show Debug Details", st.session_state.show_debug_info)
        
        if st.session_state.show_debug_info:
            st.divider()
            
            # Show message history
            st.subheader("Messages in Session State")
            for i, msg in enumerate(st.session_state.messages):
                st.write(f"**Message {i}** (role: {msg['role']})")
                st.code(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
                
                # Show a preview of how it should render
                with st.expander(f"Preview rendering of message {i}", expanded=False):
                    st.markdown(msg['content'])
            
            # Show other debug info
            debug_option = st.selectbox(
                "Select debug information to view:",
                ["Tool Outputs", "Raw Response", "Session State"]
            )
            
            if debug_option == "Tool Outputs":
                st.subheader("Tool Outputs")
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                st.json(st.session_state.tool_outputs, expanded=False)
                
            elif debug_option == "Raw Response":
                st.subheader("Last Raw Response")
                if 'last_raw_response' in st.session_state:
                    st.text_area("Content", 
                                st.session_state.get('last_raw_response', '')[:2000], 
                                height=150)
                                
            elif debug_option == "Session State":
                st.subheader("Session State")
                # Show select keys from session state
                important_keys = ["session_id", "session_initialized", "processing_message"]
                for key in important_keys:
                    if key in st.session_state:
                        st.write(f"**{key}:** {st.session_state[key]}")