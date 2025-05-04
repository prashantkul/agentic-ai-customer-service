"""
Database operations for the BetterSale customer service application.
"""

import logging
import datetime
import uuid
import json
from typing import List, Dict, Optional, Any

from .models import (
    Session, Customer, Product, CartItem, Order, OrderItem, 
    Address, CommunicationPreferences, SportsProfile, Appointment
)

# Set up logging
logger = logging.getLogger(__name__)

# ----- Customer Operations -----

def get_customer_information(customer_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a customer.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Comprehensive customer information
    """
    session = Session()
    
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return {"error": "Customer not found"}
        
        # Get billing address
        billing_address = session.query(Address).filter(
            Address.customer_id == customer_id
        ).first()
        
        # Construct a comprehensive response
        customer_data = {
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "phone": customer.phone_number,
            "membership_level": _determine_membership_level(customer.loyalty_points),
            "customer_since": customer.customer_start_date,
            "address": {
                "street": billing_address.street if billing_address else "",
                "city": billing_address.city if billing_address else "",
                "state": billing_address.state if billing_address else "",
                "zip": billing_address.zip if billing_address else "",
                "country": "USA"  # Default for demo
            },
            "preferences": {
                "favorite_sports": customer.sports_profile.preferred_sports if customer.sports_profile else [],
                "communication_preference": "Email"  # Default for demo
            },
            "loyalty": {
                "points": customer.loyalty_points,
                "member_since": customer.customer_start_date,
                "tier": _determine_membership_level(customer.loyalty_points)
            }
        }
        
        return customer_data
    
    finally:
        session.close()

def _determine_membership_level(points: int) -> str:
    """Determine membership level based on loyalty points."""
    if points >= 5000:
        return "Platinum"
    elif points >= 1000:
        return "Gold"
    elif points >= 500:
        return "Silver"
    else:
        return "Standard"

def get_order_history(customer_id: str, order_id: str = None) -> List[Dict[str, Any]]:
    """
    Get a detailed order history for a customer, optionally filtered by order ID.
    
    Args:
        customer_id: The customer ID
        order_id: Optional order ID to filter by
        
    Returns:
        List of orders with details
    """
    session = Session()
    
    try:
        # Base query
        query = session.query(Order)
        
        # Apply filters
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
            
        if order_id:
            query = query.filter(Order.id == order_id)
            
        # Get orders
        orders = query.all()
        
        order_history = []
        for order in orders:
            # Get order items with product details
            items_data = []
            for order_item in order.items:
                product = session.query(Product).filter(Product.id == order_item.product_id).first()
                
                item_data = {
                    "product_id": order_item.product_id,
                    "name": product.name if product else "Unknown Product",
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                    "subtotal": order_item.price * order_item.quantity
                }
                items_data.append(item_data)
            
            # Format order data
            order_data = {
                "order_id": order.id,
                "date": order.order_date.strftime("%Y-%m-%d"),
                "status": order.status,
                "total": order.total,
                "items": items_data
            }
            
            order_history.append(order_data)
        
        return order_history
    
    finally:
        session.close()

def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a customer by ID.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Customer data as a dictionary, or None if not found
    """
    session = Session()
    
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return None
        
        # Get billing address
        billing_address = session.query(Address).filter(
            Address.customer_id == customer_id
        ).first()
        
        # Get communication preferences
        comm_prefs = customer.communication_preferences
        
        # Get sports profile
        sports_profile = customer.sports_profile
        
        # Get scheduled appointments
        appointments = {}
        for appt in customer.appointments:
            appointments[appt.id] = {
                "service_type": appt.service_type,
                "date": appt.date,
                "time_range": appt.time_range,
                "details": appt.details,
                "status": appt.status
            }
        
        # Construct response
        customer_data = {
            "customer_id": customer.id,
            "account_number": customer.account_number,
            "customer_first_name": customer.first_name,
            "customer_last_name": customer.last_name,
            "email": customer.email,
            "phone_number": customer.phone_number,
            "customer_start_date": customer.customer_start_date,
            "years_as_customer": _calculate_years_as_customer(customer.customer_start_date),
            "loyalty_points": customer.loyalty_points,
            "preferred_store": customer.preferred_store,
            "billing_address": {
                "street": billing_address.street if billing_address else "",
                "city": billing_address.city if billing_address else "",
                "state": billing_address.state if billing_address else "",
                "zip": billing_address.zip if billing_address else ""
            },
            "communication_preferences": {
                "email": comm_prefs.email if comm_prefs else True,
                "sms": comm_prefs.sms if comm_prefs else True,
                "push_notifications": comm_prefs.push_notifications if comm_prefs else True
            },
            "sports_profile": {
                "preferred_sports": sports_profile.preferred_sports if sports_profile else [],
                "skill_level": sports_profile.skill_level if sports_profile else {},
                "favorite_teams": sports_profile.favorite_teams if sports_profile else [],
                "interests": sports_profile.interests if sports_profile else [],
                "activity_frequency": sports_profile.activity_frequency if sports_profile else ""
            },
            "scheduled_appointments": appointments,
            "purchase_history": get_customer_purchase_history(customer_id)
        }
        
        return customer_data
    
    finally:
        session.close()

def get_customer_purchase_history(customer_id: str) -> List[Dict[str, Any]]:
    """
    Get a customer's purchase history.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        List of purchases
    """
    session = Session()
    
    try:
        orders = session.query(Order).filter(Order.customer_id == customer_id).all()
        
        purchase_history = []
        for order in orders:
            items = []
            for item in order.items:
                product = session.query(Product).filter(Product.id == item.product_id).first()
                items.append({
                    "product_id": item.product_id,
                    "name": product.name if product else "Unknown Product",
                    "quantity": item.quantity
                })
            
            purchase_history.append({
                "date": order.order_date.strftime("%Y-%m-%d"),
                "items": items,
                "total_amount": order.total
            })
        
        return purchase_history
    
    finally:
        session.close()

def _calculate_years_as_customer(start_date: str) -> int:
    """
    Calculate years as customer from start date.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        
    Returns:
        Years as customer
    """
    try:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        now = datetime.datetime.now()
        return (now - start).days // 365
    except (ValueError, TypeError):
        return 0

# ----- Cart Operations -----

def access_cart_information(customer_id: str) -> Dict[str, Any]:
    """
    Get the contents of a customer's cart.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Cart information
    """
    session = Session()
    
    try:
        # Query cart items with product details
        cart_items_query = session.query(CartItem, Product).join(
            Product, CartItem.product_id == Product.id
        ).filter(CartItem.customer_id == customer_id).all()
        
        # Format for response
        items = []
        for cart_item, product in cart_items_query:
            items.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": cart_item.quantity,
                "price": product.price
            })
        
        # Calculate subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        
        return {"cart": items, "subtotal": subtotal}
    
    finally:
        session.close()

def modify_cart(customer_id: str, items_to_add: List[Dict[str, Any]], items_to_remove: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Modify a customer's cart.
    
    Args:
        customer_id: The customer ID
        items_to_add: List of items to add (each with product_id and quantity)
        items_to_remove: List of items to remove (each with product_id)
        
    Returns:
        Status of the operation
    """
    session = Session()
    
    try:
        items_added = False
        items_removed = False
        
        # Add items to cart
        for item in items_to_add:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            # Make sure quantity is a valid number
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    quantity = 1
            except (ValueError, TypeError):
                quantity = 1
            
            # Check if product exists
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                logger.warning(f"Product {product_id} not found, cannot add to cart")
                continue
            
            # Check if item already in cart
            existing_item = session.query(CartItem).filter(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += quantity
                items_added = True
            else:
                # Add new item
                new_item = CartItem(
                    customer_id=customer_id,
                    product_id=product_id,
                    quantity=quantity
                )
                session.add(new_item)
                items_added = True
        
        # Remove items from cart
        for item in items_to_remove:
            product_id = item.get("product_id")
            
            # Delete item
            result = session.query(CartItem).filter(
                CartItem.customer_id == customer_id,
                CartItem.product_id == product_id
            ).delete()
            
            if result > 0:
                items_removed = True
        
        session.commit()
        
        return {
            "status": "success",
            "message": "Cart updated successfully.",
            "items_added": items_added,
            "items_removed": items_removed
        }
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error modifying cart: {e}")
        return {
            "status": "error",
            "message": f"Error updating cart: {str(e)}"
        }
    
    finally:
        session.close()

# ----- Inventory Operations -----

def get_inventory_status(product_id: str) -> Dict[str, Any]:
    """
    Get inventory status for a specific product.
    
    Args:
        product_id: The product ID
        
    Returns:
        Inventory information
    """
    session = Session()
    
    try:
        # Check if product exists
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return {
                "available": False,
                "quantity": 0,
                "location": "Unknown",
                "message": "Product not found"
            }
        
        # In a real application, we would query an inventory management system
        # For this demo, we'll return simulated inventory data
        
        # Generate some variation in inventory quantity based on product ID
        import hashlib
        hash_value = int(hashlib.md5(product_id.encode()).hexdigest(), 16) % 100
        quantity = hash_value if hash_value > 10 else 0
        
        # Determine availability and location
        available = quantity > 0
        location = "Main Warehouse" if available else "Out of Stock"
        
        # Get recent restock date and next shipment date
        today = datetime.datetime.now()
        last_restock = (today - datetime.timedelta(days=hash_value % 30)).strftime("%Y-%m-%d")
        next_shipment = (today + datetime.timedelta(days=(hash_value % 14) + 1)).strftime("%Y-%m-%d") if not available else None
        
        inventory_data = {
            "available": available,
            "quantity": quantity,
            "location": location,
            "last_restock": last_restock
        }
        
        if next_shipment:
            inventory_data["next_shipment"] = next_shipment
        
        return inventory_data
    
    finally:
        session.close()

# ----- Product Operations -----

def get_product_recommendations(sport_or_activity: str, customer_id: str) -> Dict[str, Any]:
    """
    Get product recommendations for a sport or activity.
    
    Args:
        sport_or_activity: The sport or activity
        customer_id: The customer ID
        
    Returns:
        Product recommendations
    """
    session = Session()
    
    try:
        # Get all products for this sport
        products = session.query(Product).filter(
            Product.sport.ilike(f"%{sport_or_activity}%")
        ).all()
        
        # Get current cart items to exclude
        cart_data = access_cart_information(customer_id)
        cart_product_ids = {item["product_id"] for item in cart_data["cart"]}
        
        # Build recommendations
        recommendations = []
        for product in products:
            if product.id not in cart_product_ids:
                recommendations.append({
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price
                })
        
        return {"recommendations": recommendations}
    
    finally:
        session.close()

def check_product_availability(product_id: str, store_id: str) -> Dict[str, Any]:
    """
    Check if a product is available at a store.
    
    Args:
        product_id: The product ID
        store_id: The store ID
        
    Returns:
        Availability information
    """
    session = Session()
    
    try:
        # Check if product exists
        product = session.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return {
                "available": False,
                "quantity": 0,
                "store": store_id
            }
        
        # In a real application, we would check a store inventory table
        # For this demo, we'll simulate availability
        if product_id == "NON-EXISTENT":
            return {
                "available": False,
                "quantity": 0,
                "store": store_id
            }
        else:
            return {
                "available": True,
                "quantity": 15,
                "store": store_id
            }
    
    finally:
        session.close()

# ----- Order Operations -----

def get_order_by_id(order_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific order by ID.
    
    Args:
        order_id: The order ID
        
    Returns:
        Order details or error if not found
    """
    session = Session()
    
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"error": "Order not found", "order_id": order_id}
        
        # Get customer info
        customer = session.query(Customer).filter(Customer.id == order.customer_id).first()
        customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown Customer"
        
        # Get order items with product details
        items_data = []
        for order_item in order.items:
            product = session.query(Product).filter(Product.id == order_item.product_id).first()
            
            item_data = {
                "product_id": order_item.product_id,
                "name": product.name if product else "Unknown Product",
                "quantity": order_item.quantity,
                "price": order_item.price,
                "subtotal": order_item.price * order_item.quantity
            }
            items_data.append(item_data)
        
        # Format order data with shipping status
        shipping_status = {
            "status": order.status,
            "estimated_delivery": None,
            "tracking_number": None
        }
        
        # Add mock shipping info for shipped/processing orders
        if order.status in ["Shipped", "Processing"]:
            import random
            from datetime import datetime, timedelta
            
            # Generate mock tracking number
            tracking = f"TRK{random.randint(10000000, 99999999)}"
            
            # Generate delivery estimate (3-5 days from order date)
            delivery_days = random.randint(3, 5)
            est_delivery = (order.order_date + timedelta(days=delivery_days)).strftime("%Y-%m-%d")
            
            shipping_status["estimated_delivery"] = est_delivery
            shipping_status["tracking_number"] = tracking
        
        # Complete order data
        order_data = {
            "order_id": order.id,
            "date": order.order_date.strftime("%Y-%m-%d"),
            "customer_id": order.customer_id,
            "customer_name": customer_name,
            "status": order.status,
            "total": order.total,
            "items": items_data,
            "item_count": len(items_data),
            "shipping": shipping_status
        }
        
        return order_data
    
    finally:
        session.close()

def create_order(customer_id: str) -> Dict[str, Any]:
    """
    Create an order from the customer's cart.
    
    Args:
        customer_id: The customer ID
        
    Returns:
        Order information
    """
    session = Session()
    
    try:
        # Get cart items
        cart_data = access_cart_information(customer_id)
        cart_items = cart_data["cart"]
        
        if not cart_items:
            return {
                "status": "error",
                "message": "Cart is empty"
            }
        
        # Create order ID
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order(
            id=order_id,
            customer_id=customer_id,
            status="Processing",
            total=cart_data["subtotal"]
        )
        session.add(order)
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            session.add(order_item)
        
        # Clear the cart
        session.query(CartItem).filter(CartItem.customer_id == customer_id).delete()
        
        # Commit changes
        session.commit()
        
        # Format response
        result = {
            "status": "success",
            "order_id": order_id,
            "order_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "items": [{"product_id": item["product_id"], "quantity": item["quantity"]} 
                     for item in cart_items],
            "order_total": order.total
        }
        
        return result
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating order: {e}")
        return {
            "status": "error",
            "message": f"Error creating order: {str(e)}"
        }
    
    finally:
        session.close()

def update_salesforce_crm(customer_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update customer records in Salesforce (mocked).
    
    Args:
        customer_id: The customer ID
        details: Order details
        
    Returns:
        Status of the operation
    """
    logger.info(f"Updating Salesforce CRM for customer ID {customer_id} with details: {details}")
    
    # If this contains order details, create the order
    if "items" in details:
        # Create the order and get the order details
        order_result = create_order(customer_id)
        
        # If order was created successfully, add its details to the response
        if order_result.get("status") == "success":
            return {
                "status": "success",
                "message": "Order created and Salesforce record updated.",
                "order_id": order_result.get("order_id"),
                "order_date": order_result.get("order_date"),
                "order_total": order_result.get("order_total"),
                "status": "Processing"
            }
    
    # Default response for non-order updates or if order creation failed
    return {
        "status": "success",
        "message": "Salesforce record updated."
    }

# ----- Service Operations -----

def schedule_service(
    customer_id: str, service_type: str, date: str, time_range: str, details: str
) -> Dict[str, Any]:
    """
    Schedule a service appointment.
    
    Args:
        customer_id: The customer ID
        service_type: Type of service (e.g., Tennis Lesson)
        date: Appointment date (YYYY-MM-DD)
        time_range: Time range (e.g., 10-11)
        details: Additional details
        
    Returns:
        Appointment information
    """
    session = Session()
    
    try:
        # Create appointment ID
        appointment_id = str(uuid.uuid4())
        
        # Create appointment
        appointment = Appointment(
            id=appointment_id,
            customer_id=customer_id,
            service_type=service_type,
            date=date,
            time_range=time_range,
            details=details
        )
        session.add(appointment)
        session.commit()
        
        # Parse time range for confirmation time
        try:
            start_time_str = time_range.split("-")[0]
            confirmation_time_str = f"{date} {start_time_str}:00"
        except Exception:
            confirmation_time_str = f"{date} {time_range}"
        
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "date": date,
            "time": time_range,
            "confirmation_time": confirmation_time_str
        }
    
    except Exception as e:
        session.rollback()
        logger.error(f"Error scheduling service: {e}")
        return {
            "status": "error",
            "message": f"Error scheduling service: {str(e)}"
        }
    
    finally:
        session.close()

def get_available_service_times(service_type: str, date: str) -> List[str]:
    """
    Get available times for a service.
    
    Args:
        service_type: Type of service
        date: The date (YYYY-MM-DD)
        
    Returns:
        List of available time slots
    """
    # In a real app, this would query a scheduling database
    if "lesson" in service_type.lower():
        return ["10-11", "11-12", "14-15", "15-16", "16-17"]  # 1-hour slots
    elif "tune-up" in service_type.lower():
        return ["9-11", "11-13", "14-16"]  # 2-hour slots
    else:
        return ["10-11", "14-15"]  # Default

# ----- Customer Support Operations -----

def send_training_tips(customer_id: str, sport: str, delivery_method: str) -> Dict[str, Any]:
    """
    Send training tips to a customer.
    
    Args:
        customer_id: The customer ID
        sport: The sport
        delivery_method: Delivery method (email or sms)
        
    Returns:
        Status of the operation
    """
    logger.info(f"Sending {sport} training tips to customer {customer_id} via {delivery_method}")
    
    # In a real app, this would send an email or SMS
    return {
        "status": "success",
        "message": f"Training tips for {sport} sent via {delivery_method}."
    }

def generate_qr_code(
    customer_id: str, discount_value: float, discount_type: str, expiration_days: int
) -> Dict[str, Any]:
    """
    Generate a discount QR code.
    
    Args:
        customer_id: The customer ID
        discount_value: Value of the discount
        discount_type: Type of discount (percentage or fixed)
        expiration_days: Days until expiration
        
    Returns:
        QR code information
    """
    logger.info(f"Generating QR code for customer {customer_id} with {discount_value} {discount_type} discount")
    
    # Calculate expiration date
    expiration_date = (datetime.datetime.now() + datetime.timedelta(days=expiration_days)).strftime("%Y-%m-%d")
    
    # In a real app, this would generate an actual QR code
    mock_qr_data = f"DISCOUNT:{discount_type}:{discount_value}:EXP:{expiration_date}:CUST:{customer_id}"
    
    return {
        "status": "success",
        "qr_code_data": mock_qr_data,
        "expiration_date": expiration_date
    }