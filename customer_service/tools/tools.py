# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# add docstring to this module
"""Tools module for the customer service agent."""

import logging
import uuid
import re  # Import re for regex matching in parse_sse_response
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> str:
    """
    Sends a link to the user's phone number to start a video session.

    Args:
        phone_number (str): The phone number to send the link to.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': 'Link sent to +12065550123'}
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

    Example:
        >>> approve_discount(discount_type='percentage', value=10.0, reason='Customer loyalty')
        '{"status": "ok"}'
    """
    logger.info(
        "Approving a %s discount of %s because %s", discount_type, value, reason
    )

    logger.info("INSIDE TOOL CALL")
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

    Example:
        >>> sync_ask_for_approval(discount_type='percentage', value=15, reason='Customer loyalty')
        '{"status": "approved"}'
    """
    logger.info(
        "Asking for approval for a %s discount of %s because %s",
        discount_type,
        value,
        reason,
    )
    return '{"status": "approved"}'


def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    Updates the Salesforce CRM with customer details or order information.

    Args:
        customer_id (str): The ID of the customer.
        details (dict): A dictionary of details to update in Salesforce (e.g., order summary, appointment details).

    Returns:
        dict: A dictionary with the status and message.

    Example (if order placed): # doctest: +SKIP
        >>> update_salesforce_crm(customer_id='123', details={
            'order_id': 'ORD-9876',
            'order_date': '2024-07-25',
            'order_total': 185.74,
            'items': [{'product_id': 'RUN-S05', 'quantity': 1}, {'product_id': 'RUN-A01', 'quantity': 1}],
            'discount_applied': '10% loyalty',
            'status': 'Processing'
            })
        {'status': 'success', 'message': 'Salesforce record updated.'}
    """
    logger.info(
        "Updating Salesforce CRM for customer ID %s with details: %s",
        customer_id,
        details,
    )
    # MOCK API RESPONSE - Replace with actual Salesforce API interaction
    return {"status": "success", "message": "Salesforce record updated."}


def access_cart_information(customer_id: str) -> dict:
    """
    Retrieves the current contents of the customer's shopping cart.

    Args:
        customer_id (str): The ID of the customer.

    Returns:
        dict: A dictionary representing the cart contents. The structure should ideally be {'cart': list_of_items, 'subtotal': float}.

    Example: # doctest: +SKIP
        >>> access_cart_information(customer_id='123')
        {'cart': [{'product_id': 'RUN-S05', 'name': 'CloudRunner Running Shoes', 'quantity': 1, 'price': 139.99}, {'product_id': 'RUN-A01', 'name': 'Running Socks (3-pack)', 'quantity': 1, 'price': 15.76}], 'subtotal': 155.75}
    """
    logger.info("Accessing cart information for customer ID: %s", customer_id)

    # MOCK API RESPONSE - Replace with actual API call to cart service/database
    # Ensure the key is 'cart' containing a list of items for compatibility with Streamlit app
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
        "subtotal": 155.75,  # Example subtotal
    }
    # In a real scenario, you would fetch this data based on customer_id
    return mock_cart


def modify_cart(
    customer_id: str, items_to_add: list[dict], items_to_remove: list[dict]
) -> dict:
    """Modifies the user's shopping cart by adding and/or removing items.

    Args:
        customer_id (str): The ID of the customer.
        items_to_add (list): A list of dictionaries, each with 'product_id' and 'quantity'.
        items_to_remove (list): A list of dictionaries, each with 'product_id' (quantity is often assumed 1 or all for removal).

    Returns:
        dict: A dictionary indicating the status of the cart modification.
    Example: # doctest: +SKIP
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'BKB-007', 'quantity': 1}], items_to_remove=[{'product_id': 'TNR-001'}])
        {'status': 'success', 'message': 'Cart updated successfully.', 'items_added': True, 'items_removed': True}
    """

    logger.info("Modifying cart for customer ID: %s", customer_id)
    logger.info("Adding items: %s", items_to_add)
    logger.info("Removing items: %s", items_to_remove)
    # MOCK API RESPONSE - Replace with actual API call to cart service/database
    # This function should interact with the persistent cart storage
    items_added_flag = bool(items_to_add)
    items_removed_flag = bool(items_to_remove)
    return {
        "status": "success",
        "message": "Cart updated successfully.",  # Or provide more details
        "items_added": items_added_flag,
        "items_removed": items_removed_flag,
    }


def get_product_recommendations(sport_or_activity: str, customer_id: str) -> dict:
    """Provides product recommendations based on the sport or activity.

    Args:
        sport_or_activity: The type of sport or activity (e.g., 'Tennis', 'Running', 'Basketball').
        customer_id: Optional customer ID for personalized recommendations.

    Returns:
        A dictionary of recommended products. Example:
        {'recommendations': [
            {'product_id': 'TEN-SHOE-01', 'name': 'ProCourt Tennis Shoes', 'description': 'Excellent stability for court movement.'},
            {'product_id': 'TEN-RAC-ADV', 'name': 'Advanced Graphite Racket', 'description': 'Great for intermediate players.'}
        ]}
    """
    logger.info(
        "Getting product recommendations for sport/activity: %s and customer %s",
        sport_or_activity,
        customer_id,
    )
    # MOCK API RESPONSE - Replace with actual API call or recommendation engine logic
    # This could query a product database based on sport_or_activity and potentially customer history
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

    # Simple filtering if recommendations are already in the mock cart (for demo purposes)
    # In a real scenario, this logic might be part of the recommendation engine
    try:
        current_cart_data = access_cart_information(customer_id)
        current_cart_ids = {
            item["product_id"] for item in current_cart_data.get("cart", [])
        }
        recommendations["recommendations"] = [
            rec
            for rec in recommendations["recommendations"]
            if rec["product_id"] not in current_cart_ids
        ]
    except Exception as e:
        logger.error(f"Could not filter recommendations based on cart: {e}")

    return recommendations


def check_product_availability(product_id: str, store_id: str) -> dict:
    """Checks the availability of a product at a specified store (or for pickup).

    Args:
        product_id: The ID of the product to check.
        store_id: The ID of the store (or 'pickup' for general online availability/pickup).

    Returns:
        A dictionary indicating availability. Example:
        {'available': True, 'quantity': 10, 'store': 'Main Store'}

    Example: # doctest: +SKIP
        >>> check_product_availability(product_id='RUN-S05', store_id='pickup')
        {'available': True, 'quantity': 10, 'store': 'pickup'}
    """
    logger.info(
        "Checking availability of product ID: %s at store/location: %s",
        product_id,
        store_id,
    )
    # MOCK API RESPONSE - Replace with actual inventory system call
    # Simulate different availability based on product ID
    if product_id == "NON-EXISTENT":
        return {"available": False, "quantity": 0, "store": store_id}
    else:
        return {
            "available": True,
            "quantity": 15,
            "store": store_id,
        }  # Assume most items are available


def schedule_service(
    customer_id: str, service_type: str, date: str, time_range: str, details: str
) -> dict:
    """Schedules a service appointment (e.g., tennis lesson, bike tune-up).

    Args:
        customer_id: The ID of the customer.
        service_type: The type of service (e.g., 'Tennis Lesson', 'Bike Tune-up', 'Ski Tuning').
        date:  The desired date (YYYY-MM-DD).
        time_range: The desired time range (e.g., "10-11", "14-15").
        details: Any additional details (e.g., "Focus on backhand", "Road bike", "Waxing needed").

    Returns:
        A dictionary indicating the status of the scheduling. Example:
        {'status': 'success', 'appointment_id': '12345', 'date': '2024-07-29', 'time': '10:00 AM - 11:00 AM'}

    Example: # doctest: +SKIP
        >>> schedule_service(customer_id='123', service_type='Tennis Lesson', date='2024-07-29', time_range='10-11', details='Intermediate level')
        {'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-29', 'time': '10-11', 'confirmation_time': '2024-07-29 10:00'}
    """
    logger.info(
        "Scheduling %s service for customer ID: %s on %s (%s)",
        service_type,
        customer_id,
        date,
        time_range,
    )
    logger.info("Details: %s", details)
    # MOCK API RESPONSE - Replace with actual API call to your scheduling system
    # Calculate confirmation time based on date and time_range
    try:
        start_time_str = time_range.split("-")[0]  # Get the start time (e.g., "10")
        confirmation_time_str = (
            f"{date} {start_time_str}:00"  # e.g., "2024-07-29 10:00"
        )
    except Exception:
        confirmation_time_str = (
            f"{date} {time_range}"  # Fallback if format is different
        )

    return {
        "status": "success",
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        "confirmation_time": confirmation_time_str,  # formatted time for calendar
    }


def get_available_service_times(service_type: str, date: str) -> list:
    """Retrieves available service time slots for a given date and service type.

    Args:
        service_type: The type of service (e.g., 'Tennis Lesson', 'Bike Tune-up').
        date: The date to check (YYYY-MM-DD).

    Returns:
        A list of available time ranges.

    Example: # doctest: +SKIP
        >>> get_available_service_times(service_type='Tennis Lesson', date='2024-07-29')
        ['10-11', '14-15', '16-17']
    """
    logger.info("Retrieving available %s times for %s", service_type, date)
    # MOCK API RESPONSE - Replace with actual API call to scheduling system
    # Example slots might vary based on service type
    if "lesson" in service_type.lower():
        return ["10-11", "11-12", "14-15", "15-16", "16-17"]  # 1-hour slots
    elif "tune-up" in service_type.lower():
        return ["9-11", "11-13", "14-16"]  # 2-hour slots
    else:
        return ["10-11", "14-15"]  # Default


def send_training_tips(customer_id: str, sport: str, delivery_method: str) -> dict:
    """Sends an email or SMS with training tips for a specific sport.

    Args:
        customer_id:  The ID of the customer.
        sport: The type of sport (e.g., 'Tennis', 'Running').
        delivery_method: 'email' (default) or 'sms'.

    Returns:
        A dictionary indicating the status.

    Example: # doctest: +SKIP
        >>> send_training_tips(customer_id='123', sport='Running', delivery_method='email')
        {'status': 'success', 'message': 'Training tips for Running sent via email.'}
    """
    logger.info(
        "Sending training tips for %s to customer: %s via %s",
        sport,
        customer_id,
        delivery_method,
    )
    # MOCK API RESPONSE - Replace with actual API call or email/SMS sending logic
    # Could fetch tips from a database based on 'sport'
    return {
        "status": "success",
        "message": f"Training tips for {sport} sent via {delivery_method}.",
    }


def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """Generates a QR code for a discount.

    Args:
        customer_id: The ID of the customer.
        discount_value: The value of the discount (e.g., 10 for 10% or 5 for $5).
        discount_type: "percentage" (default) or "fixed".
        expiration_days: Number of days until the QR code expires.

    Returns:
        A dictionary containing the QR code data (or a link to it). Example:
        {'status': 'success', 'qr_code_data': '...', 'expiration_date': '2024-08-28'}

    Example: # doctest: +SKIP
        >>> generate_qr_code(customer_id='123', discount_value=15.0, discount_type='percentage', expiration_days=30)
        {'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': 'YYYY-MM-DD'}
    """
    logger.info(
        "Generating QR code for customer: %s with %s %s discount.",
        customer_id,
        discount_value,
        discount_type,
    )
    # MOCK API RESPONSE - Replace with actual QR code generation library (e.g., qrcode)
    expiration_date = (datetime.now() + timedelta(days=expiration_days)).strftime(
        "%Y-%m-%d"
    )
    # In a real app, you'd generate an actual QR code image or data URI
    mock_qr_data = f"DISCOUNT:{discount_type}:{discount_value}:EXP:{expiration_date}:CUST:{customer_id}"
    return {
        "status": "success",
        "qr_code_data": mock_qr_data,  # Replace with actual QR code data/URL
        "expiration_date": expiration_date,
    }
