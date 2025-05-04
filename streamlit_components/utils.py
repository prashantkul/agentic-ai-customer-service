"""
Utility functions for the Streamlit app.
"""

import json
import logging
import re
import requests
import streamlit as st
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure we have a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info("==== STREAMLIT UTILS MODULE INITIALIZED ====")

def call_agent_api(url, payload, headers, timeout=45):
    """Handles POST requests to the agent API and basic error checking."""
    logger.info(f"POST Request to: {url}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Payload: {json.dumps(payload)}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        logger.info(f"Response Body (first 500 chars): {response.text[:500]}")
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Error response status: {e.response.status_code}")
            logger.error(f"Error response body: {e.response.text[:500]}")
        raise


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
                                
                            # For access_cart_information specifically, also store the tool result
                            if tool_name == "access_cart_information":
                                logger.info(f"Found access_cart_information result in functionResponse")
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
    
    try:
        # Handle dictionary format with "cart" key
        if isinstance(cart_data, dict):
            if "cart" in cart_data:
                st.session_state.cart = cart_data["cart"]  # Extract the cart items list
                logger.info(f"Cart updated in session state from dict: {st.session_state.cart}")
                
                # If dict includes subtotal, store it
                if "subtotal" in cart_data:
                    st.session_state.cart_subtotal = cart_data["subtotal"]
                    
                return True
            else:
                # If dict doesn't have "cart" key but looks like a direct cart item
                # (This handles if agent returns a single item instead of a list)
                if any(key in cart_data for key in ["product_id", "name", "quantity", "price"]):
                    st.session_state.cart = [cart_data]  # Wrap in list since it's a single item
                    logger.info(f"Cart updated with single item: {st.session_state.cart}")
                    return True
                    
        # Handle list format
        elif isinstance(cart_data, list):
            st.session_state.cart = cart_data
            logger.info(f"Cart updated in session state from list: {st.session_state.cart}")
            
            # Calculate subtotal from the items
            subtotal = 0.0
            for item in cart_data:
                if isinstance(item, dict) and "price" in item and "quantity" in item:
                    try:
                        price = float(item["price"])
                        quantity = int(item["quantity"])
                        subtotal += price * quantity
                    except (ValueError, TypeError):
                        logger.warning(f"Could not calculate item subtotal for: {item}")
                        
            st.session_state.cart_subtotal = subtotal
            return True
            
        # Handle string responses (might be JSON string)
        elif isinstance(cart_data, str):
            try:
                # Try to parse as JSON
                parsed_data = json.loads(cart_data)
                logger.info(f"Parsed string cart data: {parsed_data}")
                return update_cart_display(parsed_data)  # Recursively call with parsed data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse cart data string as JSON: {e}")
        
        # If cart is empty or None, initialize as empty list
        elif cart_data is None:
            st.session_state.cart = []
            st.session_state.cart_subtotal = 0.0
            logger.info("Cart initialized as empty")
            return True
            
        # If we get here, format wasn't recognized
        logger.warning(f"Received unexpected cart data format: {type(cart_data)}")
        logger.warning(f"Cart data content: {cart_data}")
        
        # As a fallback to avoid completely broken UI, ensure cart is at least initialized
        if "cart" not in st.session_state:
            st.session_state.cart = []
            
        return False
    except Exception as e:
        logger.error(f"Error updating cart display: {e}")
        # Ensure cart exists to avoid UI errors
        if "cart" not in st.session_state:
            st.session_state.cart = []
        return False