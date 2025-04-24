# /Users/pskulkarni/Documents/source-code/customer-service/streamlit_app.py
# streamlit_app.py (Main Chat Page)
import streamlit as st
import time
import requests
import os
import uuid
import json
import logging
import pandas as pd
import re  # Add this import for regex in parse_sse_response

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

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
AGENT_BASE_URL = os.getenv(
    "AGENT_BASE_URL", "https://customer-service-agent-190206934161.us-central1.run.app"
)
AGENT_RUN_PATH = "/run_sse"
AGENT_SESSION_PATH_TEMPLATE = "/apps/{app_name}/users/{user_id}/sessions/{session_id}"
AGENT_APP_NAME = os.getenv("AGENT_APP_NAME", "customer-service-agent-app")
# AUTH_TOKEN = os.getenv("AGENT_AUTH_TOKEN") # Uncomment if needed


# --- Helper Function for API Calls ---
def call_agent_api(url, payload, headers, timeout=45):
    """Handles POST requests to the agent API and basic error checking."""
    logger.info(f"POST Request to: {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {json.dumps(payload)}")
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    logger.info(f"Response Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")
    response.raise_for_status()
    return response


def parse_sse_response(response_text):
    """Parses SSE response, extracting content and tool results."""
    assistant_reply = None
    tool_outputs = {}  # Store results keyed by tool name or invocation ID
    raw_data = response_text.strip()
    messages = [msg.strip() for msg in raw_data.split("data:") if msg.strip()]
    json_string = ""
    
    # Add more detailed logging at info level for debugging
    logger.info(f"--- Parsing SSE Response (Message Count: {len(messages)}) ---")
    logger.info(f"Raw SSE Data Sample: {raw_data[:500]}...")
    
    # Track tool calls for debugging
    found_tool_calls = False
    
    # Look for order confirmation patterns
    order_confirmed = False
    
    for json_string in messages:
        try:
            agent_data = json.loads(json_string)
            
            # Extract text content
            if (
                "content" in agent_data
                and isinstance(agent_data.get("content"), dict)
                and "parts" in agent_data.get("content", {})
            ):
                text_part = (
                    agent_data.get("content", {}).get("parts", [{}])[0].get("text")
                )
                if text_part:
                    assistant_reply = text_part.strip()
                    logger.info(f"Extracted assistant reply: {assistant_reply}")
                    
                    # Check for order confirmation in the assistant's reply
                    reply_lower = assistant_reply.lower()
                    if any(phrase in reply_lower for phrase in [
                        "order confirmed", "order has been placed", "order is confirmed", 
                        "successfully placed your order", "order has been submitted",
                        "order id", "order number", "order processed"
                    ]):
                        logger.info("Order confirmation detected in assistant reply")
                        order_confirmed = True

            # --- Enhanced Tool Result Extraction ---
            # Look for tool calls in different possible locations in the response
            
            # Check standard 'actions' field
            actions = agent_data.get("actions")
            if isinstance(actions, list):  # Handle if actions is a list
                actions = actions[0]  # Assume first action if list

            if isinstance(actions, dict):
                logger.info(f"Found 'actions' field in agent data: {json.dumps(actions)}") 
                
                # Look for tool_code/tool_result pattern
                tool_code = actions.get("tool_code")
                tool_result = actions.get("tool_result")

                if tool_code and tool_result:
                    found_tool_calls = True
                    # Extract tool name (simple regex, might need adjustment)
                    tool_name_match = re.search(r"(\w+)\(", tool_code)
                    if tool_name_match:
                        tool_name = tool_name_match.group(1)
                        logger.info(f"Found potential result for tool: {tool_name}")
                        # Attempt to parse the result as JSON
                        try:
                            parsed_result = json.loads(tool_result)
                            tool_outputs[tool_name] = parsed_result
                            logger.info(
                                f"Successfully parsed and stored JSON result for {tool_name}: {parsed_result}"
                            )
                        except json.JSONDecodeError:
                            # Store as string if not valid JSON
                            tool_outputs[tool_name] = tool_result
                            logger.warning(
                                f"Tool result for {tool_name} is not valid JSON, storing as string: {tool_result}"
                            )
                    else:
                        logger.warning(
                            f"Could not extract tool name from tool_code: {tool_code}"
                        )
                
                # Alternative: Check for function_call pattern (common in some API responses)
                function_call = actions.get("function_call")
                if isinstance(function_call, dict):
                    found_tool_calls = True
                    tool_name = function_call.get("name")
                    function_args = function_call.get("arguments", "{}")
                    
                    if tool_name:
                        logger.info(f"Found function_call for tool: {tool_name}")
                        try:
                            # Arguments might be a JSON string or already parsed
                            if isinstance(function_args, str):
                                parsed_args = json.loads(function_args)
                            else:
                                parsed_args = function_args
                                
                            # For access_cart_information specifically
                            if tool_name == "access_cart_information":
                                # Look for accompanying tool result
                                function_result = actions.get("function_result", "{}")
                                if function_result:
                                    try:
                                        if isinstance(function_result, str):
                                            parsed_result = json.loads(function_result)
                                        else:
                                            parsed_result = function_result
                                        tool_outputs[tool_name] = parsed_result
                                        logger.info(f"Found result for {tool_name}: {parsed_result}")
                                    except json.JSONDecodeError:
                                        tool_outputs[tool_name] = function_result
                                        logger.warning(f"Non-JSON result for {tool_name}: {function_result}")
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse function arguments: {function_args}")
            
            # Check for new function call format in content.parts
            if "content" in agent_data and isinstance(agent_data.get("content"), dict):
                content = agent_data.get("content", {})
                parts = content.get("parts", [])
                
                for part in parts:
                    # Check for functionCall
                    if part.get("functionCall"):
                        function_call = part.get("functionCall")
                        found_tool_calls = True
                        tool_name = function_call.get("name")
                        logger.info(f"Found functionCall for tool: {tool_name}")
                        
                        # Store args for reference - might need them later
                        function_args = function_call.get("args", {})
                        logger.info(f"Function args: {function_args}")
                        
                    # Check for functionResponse
                    if part.get("functionResponse"):
                        function_response = part.get("functionResponse")
                        response_id = function_response.get("id")
                        
                        # The response could be in different locations depending on the API format
                        response_data = None
                        
                        # Try common locations for the response data
                        if function_response.get("response"):
                            response_data = function_response.get("response")
                        elif function_response.get("result"):
                            response_data = function_response.get("result")
                        elif function_response.get("content"):
                            response_data = function_response.get("content")
                            
                        # If we found response data, try to parse it
                        if response_data:
                            logger.info(f"Found functionResponse with id: {response_id}")
                            try:
                                # The response might be a string or already parsed object
                                if isinstance(response_data, str):
                                    try:
                                        parsed_response = json.loads(response_data)
                                    except json.JSONDecodeError:
                                        # If not valid JSON, use as-is
                                        parsed_response = response_data
                                else:
                                    parsed_response = response_data
                                    
                                # Store the response under the appropriate tool name
                                if tool_name:
                                    tool_outputs[tool_name] = parsed_response
                                    logger.info(f"Parsed response for {tool_name}: {parsed_response}")
                                    
                                    # For access_cart_information specifically, also store the tool result
                                    if tool_name == "access_cart_information":
                                        logger.info(f"Found access_cart_information result in functionResponse")
                                # Fallback if we can't determine the tool name but can identify cart data
                                elif "cart" in str(parsed_response).lower():
                                    tool_outputs["access_cart_information"] = parsed_response
                                    logger.info(f"Identified cart data in response without tool name")
                            except (json.JSONDecodeError, TypeError) as e:
                                logger.warning(f"Error parsing function response: {e}")
                                if tool_name:
                                    tool_outputs[tool_name] = response_data
                                    logger.warning(f"Using raw response for {tool_name}: {response_data}")
            
            # Also check for tool_calls field (newer API pattern)
            tool_calls = agent_data.get("tool_calls", [])
            if isinstance(tool_calls, list) and tool_calls:
                found_tool_calls = True
                for tool_call in tool_calls:
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("args", {})
                        tool_response = tool_call.get("response")
                        
                        if tool_name and tool_response:
                            logger.info(f"Found tool_call response for: {tool_name}")
                            try:
                                if isinstance(tool_response, str):
                                    parsed_response = json.loads(tool_response)
                                else:
                                    parsed_response = tool_response
                                tool_outputs[tool_name] = parsed_response
                                logger.info(f"Parsed response for {tool_name}: {parsed_response}")
                            except json.JSONDecodeError:
                                tool_outputs[tool_name] = tool_response
                                logger.warning(f"Non-JSON response for {tool_name}: {tool_response}")

            # --- End Enhanced Tool Result Extraction ---

        except json.JSONDecodeError as json_err:
            logger.warning(f"Skipping non-JSON part: {json_string[:100]}... Error: {json_err}")
            continue
            
    # Log summary of what we found
    if not found_tool_calls:
        logger.warning("No tool calls found in the response")
    logger.info(f"Extracted tool outputs: {list(tool_outputs.keys())}")
    
    # Check for order confirmation via update_salesforce_crm tool
    if "update_salesforce_crm" in tool_outputs:
        logger.info("Order confirmation detected via update_salesforce_crm tool call")
        order_confirmed = True
        
        # Store order details for confirmation display
        if 'order_details' not in st.session_state:
            st.session_state.order_details = tool_outputs["update_salesforce_crm"]
    
    # Return order confirmation status as well
    return assistant_reply, tool_outputs, order_confirmed


def update_cart_display(cart_data):
    """Updates the st.session_state.cart based on fetched data."""
    logger.info(f"Received cart_data of type {type(cart_data)}: {cart_data}")
    
    if isinstance(cart_data, dict) and "cart" in cart_data:
        st.session_state.cart = cart_data["cart"]  # Extract the cart items list
        logger.info(f"Cart updated in session state from dict: {st.session_state.cart}")
        return True
    elif isinstance(cart_data, list):  # If the tool returns the list directly
        st.session_state.cart = cart_data
        logger.info(f"Cart updated in session state from list: {st.session_state.cart}")
        return True
    elif isinstance(cart_data, str):  # Handle string responses (might be JSON string)
        try:
            # Try to parse as JSON
            parsed_data = json.loads(cart_data)
            logger.info(f"Parsed string cart data: {parsed_data}")
            
            if isinstance(parsed_data, dict) and "cart" in parsed_data:
                st.session_state.cart = parsed_data["cart"]
                return True
            elif isinstance(parsed_data, list):
                st.session_state.cart = parsed_data
                return True
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cart data string as JSON: {e}")
    
    # If we get here, format wasn't recognized
    logger.warning(f"Received unexpected cart data format: {type(cart_data)}")
    logger.warning(f"Cart data content: {cart_data}")
    return False


# --- Chat & Cart Implementation ---

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.session_initialized = False
if "cart" not in st.session_state:
    st.session_state.cart = []
if "last_agent_response_data" not in st.session_state:
    st.session_state.last_agent_response_data = None
if "processing_message" not in st.session_state:
    st.session_state.processing_message = False  # Flag to prevent re-entry

# --- Main Layout (Chat on Left, Sidebar for Cart/Details) ---
col_chat, col_sidebar = st.columns([3, 1])

with col_chat:
    st.subheader("Conversation")
    # Display existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- Sidebar for Cart and Actions ---
with col_sidebar:
    # Show order confirmation if an order was just submitted
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
    
    st.subheader("🛒 Your Cart")
    if 'order_submitted' in st.session_state and st.session_state.order_submitted:
        st.info("Your cart has been submitted as an order.")
    elif st.session_state.cart:
        try:
            cart_df = pd.DataFrame(st.session_state.cart)
            if not cart_df.empty:
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
                else:
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

                    # Calculate total if possible
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
            else:
                st.info("Your cart is empty.")
        except Exception as e:
            logger.error(f"Error displaying cart DataFrame: {e}")
            st.error("Could not display cart contents.")
            st.json(st.session_state.cart)
    else:
        st.info("Your cart is empty.")

    st.divider()
    st.subheader("Actions")
    
    # Only show action buttons if the order hasn't been submitted
    if not ('order_confirmed' in st.session_state and st.session_state.order_confirmed):
        # Handle different order submission states
        if 'order_submission_state' in st.session_state and st.session_state.order_submission_state == 'confirming':
            # Show confirmation UI
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
        else:
            # Show regular action buttons
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
    
    # Debug section
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
                
            with st.expander("Tool Outputs History"):
                st.json(st.session_state.tool_outputs)
    
    st.divider()

# --- Process User Input ---
if prompt := st.chat_input("Enter your message..."):
    if not st.session_state.processing_message:  # Prevent processing if already running
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# --- Agent Interaction Logic ---
# Check if the last message is from the user and not currently processing
if (
    st.session_state.messages[-1]["role"] == "user"
    and not st.session_state.processing_message
):
    st.session_state.processing_message = True  # Set flag
    user_prompt = st.session_state.messages[-1]["content"]
    assistant_response_text = None
    cart_needs_refresh = False
    is_system_message = user_prompt.startswith("SYSTEM_")

    # Determine if this interaction likely modified the cart or is a request to view it
    prompt_lower = user_prompt.lower()
    if (
        any(
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
        or is_system_message
    ):
        cart_needs_refresh = True

    try:
        session_id = st.session_state.session_id
        user_id = "streamlit_user"
        headers = {"Content-Type": "application/json"}
        # Add Auth header if needed: headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

        # --- Step 1: Ensure Session Exists (ONLY ONCE per Streamlit session) ---
        if not st.session_state.get("session_initialized", False):
            logger.info(f"Initializing session {session_id} for user {user_id}")
            session_path = AGENT_SESSION_PATH_TEMPLATE.format(
                app_name=AGENT_APP_NAME, user_id=user_id, session_id=session_id
            )
            session_url = f"{AGENT_BASE_URL}{session_path}"
            session_payload = {"state": {}}
            session_response = call_agent_api(
                session_url, session_payload, headers, timeout=15
            )
            st.session_state.session_initialized = True
            logger.info(f"Session {session_id} initialized successfully.")

        # --- Step 2: Run the Agent with the Prompt ---
        run_url = f"{AGENT_BASE_URL}{AGENT_RUN_PATH}"
        # Use a specific prompt for system messages like refresh
        effective_prompt = user_prompt
        if user_prompt == "SYSTEM_FETCH_CART":
            effective_prompt = "Use the access_cart_information tool to show what's in my cart."
        elif user_prompt == "SYSTEM_FETCH_CART_INTERNAL":
            effective_prompt = "Run access_cart_information and return the current contents of my shopping cart."

        run_payload = {
            "app_name": AGENT_APP_NAME,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {"role": "user", "parts": [{"text": effective_prompt}]},
            "streaming": False,
        }

        logger.info(f"Attempting run POST to: {run_url}")
        with st.spinner("Thinking..."):
            response = call_agent_api(run_url, run_payload, headers, timeout=45)
            # Store raw response for debugging
            st.session_state.last_raw_response = response.text[:10000]  # Limit size
            assistant_response_text, tool_outputs, order_confirmed = parse_sse_response(response.text)
            
            # Store tool outputs for debugging
            if tool_outputs:
                if 'tool_outputs' not in st.session_state:
                    st.session_state.tool_outputs = {}
                for tool_name, output in tool_outputs.items():
                    st.session_state.tool_outputs[tool_name] = output
                    
            # Handle order confirmation
            if order_confirmed:
                st.session_state.order_confirmed = True
                
                # Clear the cart after successful order submission
                if 'order_submission_state' in st.session_state and st.session_state.order_submission_state == 'confirmed':
                    # We'll keep the cart data for the order summary, but mark it as submitted
                    st.session_state.order_submitted = True
                    
                    # Reset the order submission state
                    st.session_state.order_submission_state = None

            # --- Step 3: Explicitly Refresh Cart if Needed ---
            # Check if the access_cart_information tool was called AND returned data
            if "access_cart_information" in tool_outputs:
                logger.info(f"Found access_cart_information in tool_outputs: {tool_outputs['access_cart_information']}")
                update_success = update_cart_display(tool_outputs["access_cart_information"])
                if update_success:
                    cart_needs_refresh = False  # Already refreshed via tool output
                    logger.info("Cart display updated successfully")
                else:
                    logger.warning("Failed to update cart display from tool output")
            # Or, if the response suggests a change but the tool didn't run/return cart
            elif cart_needs_refresh and not is_system_message:
                logger.info("Response suggests cart change, explicitly fetching cart.")
                fetch_cart_payload = {
                    "app_name": AGENT_APP_NAME,
                    "user_id": user_id,
                    "session_id": session_id,
                    "new_message": {
                        "role": "user",
                        "parts": [{"text": "SYSTEM_FETCH_CART_INTERNAL"}],
                    },  # Internal trigger
                    "streaming": False,
                }
                try:
                    # Use a shorter timeout for this potentially quick call
                    fetch_response = call_agent_api(
                        run_url, fetch_cart_payload, headers, timeout=20
                    )
                    _, fetch_tool_outputs, _ = parse_sse_response(fetch_response.text)
                    if "access_cart_information" in fetch_tool_outputs:
                        logger.info(f"Explicit cart fetch received: {fetch_tool_outputs['access_cart_information']}")
                        update_success = update_cart_display(
                            fetch_tool_outputs["access_cart_information"]
                        )
                        if update_success:
                            logger.info("Cart display updated successfully from explicit fetch")
                        else:
                            logger.warning("Failed to update cart display from explicit fetch")
                    else:
                        logger.warning(
                            "Explicit cart fetch did not return expected tool output. Available keys: " + 
                            str(list(fetch_tool_outputs.keys()))
                        )
                except Exception as fetch_err:
                    logger.error(f"Failed to explicitly fetch cart: {fetch_err}")
                    # Don't overwrite the main assistant response if fetch fails

            # Handle case where no text response was found
            if assistant_response_text is None:
                if is_system_message:  # Don't show system messages to user
                    assistant_response_text = None  # Suppress output
                else:
                    logger.warning("No text content message found in the response.")
                    assistant_response_text = (
                        "I processed your request, but didn't generate a text response."
                    )

    # --- Error Handling (Consolidated) ---
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Request failed: {e.request.method} {e.request.url}", exc_info=True
        )
        if e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response Body: {e.response.text}")
        st.error(f"Error contacting agent service: {e}")
        assistant_response_text = "Sorry, I encountered an error communicating with the service. Please try again."
    except json.JSONDecodeError as e:
        st.error(f"Error decoding agent response: {e}. Check logs for details.")
        logger.error(f"Failed to decode JSON during SSE parsing.", exc_info=True)
        assistant_response_text = (
            "Sorry, the response from the agent was not in the expected format."
        )
    except Exception as e:
        logger.error("An unexpected error occurred", exc_info=True)
        st.error(f"An unexpected error occurred: {e}")
        assistant_response_text = "Sorry, an unexpected error happened on my end."
    finally:
        st.session_state.processing_message = False  # Release flag

    # --- Finalize Interaction ---
    # Add assistant response to history if one exists and it wasn't a system message
    if assistant_response_text and not is_system_message:
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response_text}
        )
        # st.session_state.last_agent_response_data = full_agent_response_data # Storing raw data might be less useful now
        st.rerun()  # Rerun to display the new assistant message and potentially updated cart
