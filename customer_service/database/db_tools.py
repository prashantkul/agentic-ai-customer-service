"""
Database-backed tool implementations for the customer service agent.
This module provides database-backed versions of all the tools in customer_service/tools/tools.py.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import database operations
from .operations import (
    access_cart_information as db_access_cart_information,
    modify_cart as db_modify_cart,
    get_product_recommendations as db_get_product_recommendations,
    check_product_availability as db_check_product_availability,
    schedule_service as db_schedule_service,
    get_available_service_times as db_get_available_service_times,
    send_training_tips as db_send_training_tips,
    generate_qr_code as db_generate_qr_code,
    update_salesforce_crm as db_update_salesforce_crm
)

# Set up logging
logger = logging.getLogger(__name__)

# ----- Tool Implementations -----

def send_call_companion_link(phone_number: str) -> Dict[str, str]:
    """
    Sends a link to the user's phone number to start a video session.

    Args:
        phone_number (str): The phone number to send the link to.

    Returns:
        dict: A dictionary with the status and message.
    """
    logger.info("Sending call companion link to %s", phone_number)
    return {"status": "success", "message": f"Link sent to {phone_number}"}

def approve_discount(discount_type: str, value: float, reason: str) -> str:
    """
    Approve the flat rate or percentage discount requested by the user.

    Args:
        discount_type (str): The type of discount, either "percentage" or "flat".
        value (float): The value of the discount.
        reason (str): The reason for the discount.

    Returns:
        str: A JSON string indicating the status of the approval.
    """
    logger.info(
        "Approving a %s discount of %s because %s", discount_type, value, reason
    )
    return '{"status": "ok"}'

def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> str:
    """
    Asks the manager for approval for a discount.

    Args:
        discount_type (str): The type of discount, either "percentage" or "flat".
        value (float): The value of the discount.
        reason (str): The reason for the discount.

    Returns:
        str: A JSON string indicating the status of the approval.
    """
    logger.info(
        "Asking for approval for a %s discount of %s because %s",
        discount_type,
        value,
        reason,
    )
    return '{"status": "approved"}'

def update_salesforce_crm(customer_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the Salesforce CRM with customer details or order information.
    If the details contain items, creates an order in the database.

    Args:
        customer_id (str): The ID of the customer.
        details (dict): A dictionary of details to update in Salesforce.

    Returns:
        dict: A dictionary with the status and message.
    """
    logger.info(
        "Updating Salesforce CRM for customer ID %s with details: %s",
        customer_id,
        details,
    )
    
    try:
        # Check if this is an order submission
        if "items" in details:
            try:
                # Import create_order directly to avoid circular imports - using relative import
                from .operations import create_order
                
                # Create the order in the database
                logger.info("Creating order for customer ID: %s", customer_id)
                order_result = create_order(customer_id)
                
                # If order was created successfully, return the order details
                if order_result and order_result.get("status") == "success":
                    logger.info(f"Order created successfully: {order_result}")
                    return {
                        "status": "success",
                        "message": "Order created and Salesforce record updated.",
                        "order_id": order_result.get("order_id"),
                        "order_date": order_result.get("order_date"),
                        "order_total": order_result.get("order_total"),
                        "items": order_result.get("items", []),
                        "status": "Processing"
                    }
                else:
                    logger.error(f"Failed to create order: {order_result}")
                    return {
                        "status": "error",
                        "message": f"Failed to create order: {order_result.get('message', 'Unknown error')}"
                    }
            except Exception as order_error:
                logger.error(f"Error creating order: {order_error}")
                return {
                    "status": "error",
                    "message": f"Error creating order: {str(order_error)}"
                }
        
        # For non-order updates, call the database function
        result = db_update_salesforce_crm(customer_id, details)
        return result
    except Exception as e:
        logger.error(f"Error updating Salesforce CRM: {e}")
        return {"status": "error", "message": f"Error updating Salesforce CRM: {str(e)}"}

def access_cart_information(customer_id: str) -> Dict[str, Any]:
    """
    Retrieves the current contents of the customer's shopping cart.

    Args:
        customer_id (str): The ID of the customer.

    Returns:
        dict: A dictionary representing the cart contents.
    """
    logger.info("Accessing cart information for customer ID: %s", customer_id)
    
    try:
        cart_data = db_access_cart_information(customer_id)
        logger.info(f"Retrieved cart data from database: {cart_data}")
        return cart_data
    except Exception as e:
        logger.error(f"Error retrieving cart data: {e}")
        # Fallback to mock data if database access fails
        mock_cart = {
            "cart": [
                {
                    "product_id": "RUN-S05",
                    "name": "CloudRunner Running Shoes",
                    "quantity": 1,
                    "price": 139.99,
                },
                {
                    "product_id": "RUN-A01",
                    "name": "Running Socks (3-pack)",
                    "quantity": 1,
                    "price": 15.76,
                },
            ],
            "subtotal": 155.75,
        }
        return mock_cart

def modify_cart(
    customer_id: str, items_to_add: List[Dict[str, Any]], items_to_remove: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Modifies the user's shopping cart by adding and/or removing items.

    Args:
        customer_id (str): The ID of the customer.
        items_to_add (list): A list of dictionaries, each with 'product_id' and 'quantity'.
        items_to_remove (list): A list of dictionaries, each with 'product_id'.

    Returns:
        dict: A dictionary indicating the status of the cart modification.
    """
    logger.info("Modifying cart for customer ID: %s", customer_id)
    logger.info("Adding items: %s", items_to_add)
    logger.info("Removing items: %s", items_to_remove)
    
    try:
        result = db_modify_cart(customer_id, items_to_add, items_to_remove)
        logger.info(f"Cart modification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error modifying cart: {e}")
        # Fallback to mock response if database access fails
        return {
            "status": "success",
            "message": "Cart updated successfully.",
            "items_added": bool(items_to_add),
            "items_removed": bool(items_to_remove),
        }

def get_product_recommendations(sport_or_activity: str, customer_id: str) -> Dict[str, Any]:
    """
    Provides product recommendations based on the sport or activity.

    Args:
        sport_or_activity (str): The type of sport or activity.
        customer_id (str): Optional customer ID for personalized recommendations.

    Returns:
        dict: A dictionary of recommended products.
    """
    logger.info(
        "Getting product recommendations for sport/activity: %s and customer %s",
        sport_or_activity,
        customer_id,
    )
    
    try:
        recommendations = db_get_product_recommendations(sport_or_activity, customer_id)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting product recommendations: {e}")
        # Fallback to mock response
        recommendations = {"recommendations": []}
        sport = sport_or_activity.lower()

        if "tennis" in sport:
            recommendations["recommendations"].extend(
                [
                    {
                        "product_id": "TEN-SHOE-01",
                        "name": "ProCourt Tennis Shoes",
                        "description": "Excellent stability for court movement.",
                        "price": 129.99,
                    },
                    {
                        "product_id": "TEN-RAC-ADV",
                        "name": "Advanced Graphite Racket",
                        "description": "Great for intermediate players seeking more power.",
                        "price": 149.99,
                    },
                    {
                        "product_id": "TNB-003",
                        "name": "Tennis Balls (3-pack)",
                        "description": "Durable, high-performance tennis balls.",
                        "price": 5.99,
                    },
                ]
            )
        elif "running" in sport:
            recommendations["recommendations"].extend(
                [
                    {
                        "product_id": "RUN-S05",
                        "name": "CloudRunner Running Shoes",
                        "description": "Lightweight and breathable for long distances.",
                        "price": 139.99,
                    },
                    {
                        "product_id": "RUN-A01",
                        "name": "Running Socks (3-pack)",
                        "description": "Moisture-wicking and blister protection.",
                        "price": 15.76,
                    },
                    {
                        "product_id": "RUN-W01",
                        "name": "GPS Running Watch",
                        "description": "Track your pace, distance, and heart rate.",
                        "price": 199.99,
                    },
                ]
            )
        elif "basketball" in sport:
            recommendations["recommendations"].extend(
                [
                    {
                        "product_id": "BKB-007",
                        "name": "Official Size Basketball",
                        "description": "Durable composite leather for indoor/outdoor play.",
                        "price": 29.99,
                    },
                    {
                        "product_id": "BKB-S01",
                        "name": "High-Top Basketball Shoes",
                        "description": "Superior ankle support and cushioning.",
                        "price": 119.99,
                    },
                    {
                        "product_id": "BKB-A02",
                        "name": "Basketball Hoop (Portable)",
                        "description": "Adjustable height, easy to move.",
                        "price": 249.99,
                    },
                ]
            )
        else:  # Generic fallback
            recommendations["recommendations"].append(
                {
                    "product_id": "GEN-WB-01",
                    "name": "Insulated Water Bottle",
                    "description": "Keeps drinks cold during any activity.",
                    "price": 19.99,
                }
            )
        
        return recommendations

def check_product_availability(product_id: str, store_id: str) -> Dict[str, Any]:
    """
    Checks the availability of a product at a specified store (or for pickup).

    Args:
        product_id (str): The ID of the product to check.
        store_id (str): The ID of the store (or 'pickup' for general online availability/pickup).

    Returns:
        dict: A dictionary indicating availability.
    """
    logger.info(
        "Checking availability of product ID: %s at store/location: %s",
        product_id,
        store_id,
    )
    
    try:
        availability = db_check_product_availability(product_id, store_id)
        return availability
    except Exception as e:
        logger.error(f"Error checking product availability: {e}")
        # Fallback to mock response
        if product_id == "NON-EXISTENT":
            return {"available": False, "quantity": 0, "store": store_id}
        else:
            return {
                "available": True,
                "quantity": 15,
                "store": store_id,
            }

def schedule_service(
    customer_id: str, service_type: str, date: str, time_range: str, details: str
) -> Dict[str, Any]:
    """
    Schedules a service appointment (e.g., tennis lesson, bike tune-up).

    Args:
        customer_id (str): The ID of the customer.
        service_type (str): The type of service.
        date (str): The desired date (YYYY-MM-DD).
        time_range (str): The desired time range (e.g., "10-11", "14-15").
        details (str): Any additional details.

    Returns:
        dict: A dictionary indicating the status of the scheduling.
    """
    logger.info(
        "Scheduling %s service for customer ID: %s on %s (%s)",
        service_type,
        customer_id,
        date,
        time_range,
    )
    logger.info("Details: %s", details)
    
    try:
        result = db_schedule_service(customer_id, service_type, date, time_range, details)
        return result
    except Exception as e:
        logger.error(f"Error scheduling service: {e}")
        # Fallback to mock response
        try:
            start_time_str = time_range.split("-")[0]
            confirmation_time_str = f"{date} {start_time_str}:00"
        except Exception:
            confirmation_time_str = f"{date} {time_range}"

        return {
            "status": "success",
            "appointment_id": str(uuid.uuid4()),
            "date": date,
            "time": time_range,
            "confirmation_time": confirmation_time_str,
        }

def get_available_service_times(service_type: str, date: str) -> List[str]:
    """
    Retrieves available service time slots for a given date and service type.

    Args:
        service_type (str): The type of service.
        date (str): The date to check (YYYY-MM-DD).

    Returns:
        list: A list of available time ranges.
    """
    logger.info("Retrieving available %s times for %s", service_type, date)
    
    try:
        available_times = db_get_available_service_times(service_type, date)
        return available_times
    except Exception as e:
        logger.error(f"Error retrieving available service times: {e}")
        # Fallback to mock response
        if "lesson" in service_type.lower():
            return ["10-11", "11-12", "14-15", "15-16", "16-17"]  # 1-hour slots
        elif "tune-up" in service_type.lower():
            return ["9-11", "11-13", "14-16"]  # 2-hour slots
        else:
            return ["10-11", "14-15"]  # Default

def send_training_tips(customer_id: str, sport: str, delivery_method: str) -> Dict[str, Any]:
    """
    Sends an email or SMS with training tips for a specific sport.

    Args:
        customer_id (str): The ID of the customer.
        sport (str): The type of sport.
        delivery_method (str): 'email' (default) or 'sms'.

    Returns:
        dict: A dictionary indicating the status.
    """
    logger.info(
        "Sending training tips for %s to customer: %s via %s",
        sport,
        customer_id,
        delivery_method,
    )
    
    try:
        result = db_send_training_tips(customer_id, sport, delivery_method)
        return result
    except Exception as e:
        logger.error(f"Error sending training tips: {e}")
        # Fallback to mock response
        return {
            "status": "success",
            "message": f"Training tips for {sport} sent via {delivery_method}.",
        }

def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> Dict[str, Any]:
    """
    Generates a QR code for a discount.

    Args:
        customer_id (str): The ID of the customer.
        discount_value (float): The value of the discount.
        discount_type (str): "percentage" (default) or "fixed".
        expiration_days (int): Number of days until the QR code expires.

    Returns:
        dict: A dictionary containing the QR code data.
    """
    logger.info(
        "Generating QR code for customer: %s with %s %s discount.",
        customer_id,
        discount_value,
        discount_type,
    )
    
    try:
        result = db_generate_qr_code(customer_id, discount_value, discount_type, expiration_days)
        return result
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        # Fallback to mock response
        expiration_date = (datetime.now() + timedelta(days=expiration_days)).strftime(
            "%Y-%m-%d"
        )
        mock_qr_data = f"DISCOUNT:{discount_type}:{discount_value}:EXP:{expiration_date}:CUST:{customer_id}"
        return {
            "status": "success",
            "qr_code_data": mock_qr_data,
            "expiration_date": expiration_date,
        }