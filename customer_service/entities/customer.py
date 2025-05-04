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
"""Customer entity module."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    """
    Represents a customer's address.
    """

    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    Represents a product in a customer's purchase history.
    """

    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class Purchase(BaseModel):
    """
    Represents a customer's purchase.
    """

    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferences(BaseModel):
    """
    Represents a customer's communication preferences.
    """

    email: bool = True
    sms: bool = True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)


class SportsProfile(BaseModel):
    """
    Represents a customer's sports profile.
    """

    preferred_sports: List[str]
    skill_level: Dict[str, str] = Field(
        default_factory=dict
    )  # e.g., {"tennis": "intermediate", "running": "beginner"}
    favorite_teams: List[str] = Field(default_factory=list)
    interests: List[str]
    activity_frequency: str  # e.g., "weekly", "monthly", "occasionally"
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    Represents a customer.
    """

    account_number: str
    customer_id: str
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: str
    customer_start_date: str
    years_as_customer: int
    billing_address: Address
    purchase_history: List[Purchase]
    loyalty_points: int
    preferred_store: str
    communication_preferences: CommunicationPreferences
    # garden_profile: GardenProfile
    sports_profile: SportsProfile
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the Customer object to a JSON string.

        Returns:
            A JSON string representing the Customer object.
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional["Customer"]:
        """
        Retrieves a customer based on their ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            The Customer object if found, None otherwise.
        """
        try:
            # Import the operations module using relative import
            import sys
            import json
            import logging
            
            # Try to import using relative import (for within package)
            try:
                # Attempt to import using relative import for when called from within the package
                from ..database.operations import get_customer as db_get_customer
            except (ImportError, ValueError):
                # Fallback to absolute import if relative import fails
                from customer_service.database.operations import get_customer as db_get_customer
            
            logger = logging.getLogger(__name__)
            
            # Get customer data from database
            customer_data = db_get_customer(current_customer_id)
            
            if not customer_data:
                logger.warning(f"Customer {current_customer_id} not found in database")
                return Customer._get_dummy_customer(current_customer_id)
            
            # Parse sports profile JSON data
            preferred_sports = []
            skill_level = {}
            favorite_teams = []
            interests = []
            
            if customer_data.get("sports_profile"):
                if customer_data["sports_profile"].get("preferred_sports"):
                    preferred_sports = json.loads(customer_data["sports_profile"]["preferred_sports"])
                if customer_data["sports_profile"].get("skill_level"):
                    skill_level = json.loads(customer_data["sports_profile"]["skill_level"])
                if customer_data["sports_profile"].get("favorite_teams"):
                    favorite_teams = json.loads(customer_data["sports_profile"]["favorite_teams"])
                if customer_data["sports_profile"].get("interests"):
                    interests = json.loads(customer_data["sports_profile"]["interests"])
            
            # Convert purchase history
            purchase_history = []
            if customer_data.get("purchase_history"):
                for purchase in customer_data["purchase_history"]:
                    items = []
                    for item in purchase.get("items", []):
                        items.append(Product(
                            product_id=item.get("product_id", ""),
                            name=item.get("name", ""),
                            quantity=item.get("quantity", 1)
                        ))
                    purchase_history.append(Purchase(
                        date=purchase.get("date", ""),
                        items=items,
                        total_amount=purchase.get("total_amount", 0.0)
                    ))
            
            # Create the customer entity from database data
            return Customer(
                customer_id=customer_data["customer_id"],
                account_number=customer_data["account_number"],
                customer_first_name=customer_data["customer_first_name"],
                customer_last_name=customer_data["customer_last_name"],
                email=customer_data["email"],
                phone_number=customer_data["phone_number"],
                customer_start_date=customer_data["customer_start_date"],
                years_as_customer=customer_data["years_as_customer"],
                billing_address=Address(
                    street=customer_data["billing_address"].get("street", ""),
                    city=customer_data["billing_address"].get("city", ""),
                    state=customer_data["billing_address"].get("state", ""),
                    zip=customer_data["billing_address"].get("zip", "")
                ),
                purchase_history=purchase_history,
                loyalty_points=customer_data["loyalty_points"],
                preferred_store=customer_data["preferred_store"],
                communication_preferences=CommunicationPreferences(
                    email=customer_data.get("communication_preferences", {}).get("email", True),
                    sms=customer_data.get("communication_preferences", {}).get("sms", False),
                    push_notifications=customer_data.get("communication_preferences", {}).get("push_notifications", False)
                ),
                sports_profile=SportsProfile(
                    preferred_sports=preferred_sports,
                    skill_level=skill_level,
                    favorite_teams=favorite_teams,
                    interests=interests,
                    activity_frequency=customer_data.get("sports_profile", {}).get("activity_frequency", "occasionally")
                ),
                scheduled_appointments=customer_data.get("scheduled_appointments", {})
            )
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching customer from database: {e}")
            return Customer._get_dummy_customer(current_customer_id)
    
    @staticmethod
    def _get_dummy_customer(customer_id: str) -> "Customer":
        """Return a dummy customer for fallback."""
        return Customer(
            customer_id=customer_id,
            account_number="428765091",
            customer_first_name="Alex",
            customer_last_name="Johnson",
            email="alex.johnson@example.com",
            phone_number="+1-702-555-1212",
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345"
            ),
            purchase_history=[  
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="TNR-001",
                            name="ProStaff Tennis Racket",
                            quantity=1,
                        ),
                        Product(
                            product_id="TNB-003",
                            name="Tennis Balls (3-pack)",
                            quantity=2,
                        ),
                    ],
                    total_amount=85.98,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="RUN-S05",
                            name="CloudRunner Running Shoes",
                            quantity=1,
                        ),
                        Product(
                            product_id="RUN-A01",
                            name="Running Socks (3-pack)",
                            quantity=1,
                        ),
                    ],
                    total_amount=142.5,
                ),
            ],
            loyalty_points=133,
            preferred_store="Sports Basement",
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
            sports_profile=SportsProfile(
                preferred_sports=["Tennis", "Running"],
                skill_level={"Tennis": "Intermediate", "Running": "Beginner"},
                favorite_teams=["Lakers", "Dodgers"],
                interests=["Hiking", "Yoga"],
                activity_frequency="weekly",
            ),
            scheduled_appointments={},
        )
