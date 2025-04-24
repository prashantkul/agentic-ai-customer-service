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
        # In a real application, this would involve a database lookup.
        # For this example, we'll just return a dummy customer.
        return Customer(
            customer_id=current_customer_id,
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
            purchase_history=[  # Example purchase history
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
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="BKB-007",
                            name="Official Size Basketball",
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="NKB-007",
                            name="Nike Air Zoom Basketball Shoes",
                            quantity=1,
                        ),
                    ],
                    total_amount=155.25,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="SKB-007",
                            name="Thermal Basketball Jersey",
                            quantity=1,
                        ),
                    ],
                    total_amount=65.25,
                ),
            ],
            loyalty_points=133,
            preferred_store="Sports Basement",
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
         
            # Updated to SportsProfile with example data
            sports_profile=SportsProfile(
                preferred_sports=["Tennis", "Running"],
                skill_level={"Tennis": "Intermediate", "Running": "Beginner"},
                favorite_teams=["Lakers", "Dodgers"],
                interests=["Hiking", "Yoga"],
                activity_frequency="weekly",
            ),
            scheduled_appointments={},
        )
