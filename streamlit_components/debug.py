"""
Debug tools for the Streamlit app.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_debug_section():
    """Display debug tools and information in a more compact format."""
    # Initialize expanded state for debug section if not present
    if 'debug_section_expanded' not in st.session_state:
        st.session_state.debug_section_expanded = True
        
    # Create a manual "keep open" checkbox to control debug panel
    st.session_state.debug_section_expanded = st.checkbox(
        "🔧 Show Developer Tools", 
        value=st.session_state.debug_section_expanded,
        key="keep_debug_open"
    )
    
    # Only display debug section if expanded
    if st.session_state.debug_section_expanded:
        
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
            
            # Initialize expanded states if not present
            if 'message_preview_expanded' not in st.session_state:
                st.session_state.message_preview_expanded = {}
            
            if 'debug_tool_outputs_expanded' not in st.session_state:
                st.session_state.debug_tool_outputs_expanded = False
            
            # Show message history
            st.subheader("Messages in Session State")
            if "messages" in st.session_state and st.session_state.messages:
                for i, msg in enumerate(st.session_state.messages):
                    st.write(f"**Message {i}** (role: {msg['role']})")
                    st.code(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
                    
                    # Create a toggle for message preview
                    preview_key = f"preview_msg_{i}"
                    if preview_key not in st.session_state:
                        st.session_state[preview_key] = False
                        
                    # Use a checkbox instead of an expander for the preview
                    if st.checkbox(f"Show preview for message {i}", 
                                  value=st.session_state[preview_key], 
                                  key=f"toggle_{preview_key}"):
                        st.session_state[preview_key] = True
                        st.markdown(msg['content'])
                    else:
                        st.session_state[preview_key] = False
            else:
                st.info("No messages in session state yet.")
            
            # Store the last selected debug option
            if 'last_debug_option' not in st.session_state:
                st.session_state.last_debug_option = "Tool Outputs"
            
            # Show other debug info
            selected_option = st.selectbox(
                "Select debug information to view:",
                ["Tool Outputs", "Raw Response", "Session State"],
                index=["Tool Outputs", "Raw Response", "Session State"].index(st.session_state.last_debug_option)
            )
            
            # Store the selection
            st.session_state.last_debug_option = selected_option
            
            if selected_option == "Tool Outputs":
                st.subheader("Tool Outputs")
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                    
                # Initialize debug tool outputs expanded state if not present
                if 'debug_tool_outputs_expanded' not in st.session_state:
                    st.session_state.debug_tool_outputs_expanded = False
                
                # Add a checkbox to control expansion
                st.session_state.debug_tool_outputs_expanded = st.checkbox(
                    "Show expanded tool outputs", 
                    value=st.session_state.debug_tool_outputs_expanded,
                    key="keep_tool_outputs_expanded"
                )
                
                # Initialize tool_outputs if needed
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                    
                if st.session_state.tool_outputs:
                    st.json(st.session_state.tool_outputs, expanded=st.session_state.debug_tool_outputs_expanded)
                else:
                    st.info("No tool outputs have been recorded yet.")
                
            elif selected_option == "Raw Response":
                st.subheader("Last Raw Response")
                if 'last_raw_response' in st.session_state:
                    st.text_area("Content", 
                                st.session_state.get('last_raw_response', '')[:2000], 
                                height=150)
                                
            elif selected_option == "Session State":
                st.subheader("Session State")
                # Show select keys from session state
                important_keys = ["session_id", "session_initialized", "processing_message"]
                for key in important_keys:
                    if key in st.session_state:
                        st.write(f"**{key}:** {st.session_state[key]}")