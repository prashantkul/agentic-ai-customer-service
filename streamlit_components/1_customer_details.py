# pages/1_Customer_Details.py
import streamlit as st
from customer_service.entities.customer import (
    Customer,
    Address,
    Purchase,
    Product,
    CommunicationPreferences,
    SportsProfile,
)
from typing import Optional
import pandas as pd

# --- Page Configuration (Optional for subpages, but can set title) ---
#st.set_page_config(page_title="Customer Details", layout="wide")


# --- Helper Functions ---
def display_customer_details(customer: Optional[Customer]):
    """Displays the customer details in the Streamlit app."""
    if customer:
        st.header(
            f"Customer Details: {customer.customer_first_name} {customer.customer_last_name}"
        )
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Account Information")
            st.text(f"Customer ID: {customer.customer_id}")
            st.text(f"Account Number: {customer.account_number}")
            st.text(f"Email: {customer.email}")
            st.text(f"Phone: {customer.phone_number}")
            st.text(f"Customer Since: {customer.customer_start_date}")
            st.text(f"Years as Customer: {customer.years_as_customer}")
            st.text(f"Loyalty Points: {customer.loyalty_points}")
            st.text(f"Preferred Store: {customer.preferred_store}")

            st.subheader("Billing Address")
            st.text(f"Street: {customer.billing_address.street}")
            st.text(f"City: {customer.billing_address.city}")
            st.text(f"State: {customer.billing_address.state}")
            st.text(f"Zip: {customer.billing_address.zip}")

        with col2:
            st.subheader("Communication Preferences")
            st.checkbox(
                "Email", value=customer.communication_preferences.email, disabled=True
            )
            st.checkbox(
                "SMS", value=customer.communication_preferences.sms, disabled=True
            )
            st.checkbox(
                "Push Notifications",
                value=customer.communication_preferences.push_notifications,
                disabled=True,
            )
            st.subheader("Sports Profile") # Changed header
            st.text(f"Preferred Sports: {', '.join(customer.sports_profile.preferred_sports)}")
            # Display skill levels nicely
            skill_levels = customer.sports_profile.skill_level
            if skill_levels:
                st.text("Skill Levels:")
                for sport, level in skill_levels.items():
                    st.text(f"  - {sport}: {level}")
            st.text(f"Favorite Teams: {', '.join(customer.sports_profile.favorite_teams)}")
            st.text(f"Other Interests: {', '.join(customer.sports_profile.interests)}") # Renamed label slightly
            st.text(f"Activity Frequency: {customer.sports_profile.activity_frequency}")
            

            st.subheader("Scheduled Appointments")
            if customer.scheduled_appointments:
                # Using st.json for better display of dictionaries/lists
                st.json(customer.scheduled_appointments)
            else:
                st.info("No scheduled appointments.")  # Use info box for clarity

        st.divider()
        st.subheader("Purchase History")
        if customer.purchase_history:
            # Prepare data for display
            purchase_data = []
            for purchase in customer.purchase_history:
                for item in purchase.items:
                    purchase_data.append(
                        {
                            "Purchase Date": purchase.date,
                            "Product ID": item.product_id,
                            "Product Name": item.name,
                            "Quantity": item.quantity,
                            "Purchase Total": f"${purchase.total_amount:.2f}",  # Display total once per purchase group later if needed
                        }
                    )
            df_purchases = pd.DataFrame(purchase_data)

            # Display grouped by purchase date might be better, but simple table for now
            st.dataframe(
                df_purchases, use_container_width=True, hide_index=True
            )  # Hide index for cleaner look

            # Alternative: Display as expandable sections per purchase
            # st.write("--- Purchase Details (Expandable) ---")
            # for i, purchase in enumerate(customer.purchase_history):
            #     with st.expander(f"Purchase on {purchase.date} - Total: ${purchase.total_amount:.2f}"):
            #         items_data = [{ "Product ID": item.product_id, "Name": item.name, "Quantity": item.quantity} for item in purchase.items]
            #         st.dataframe(pd.DataFrame(items_data), hide_index=True, use_container_width=True)

        else:
            st.info("No purchase history found.")  # Use info box

    else:
        st.warning("Customer not found. Please check the ID and try again.")


# --- Streamlit App UI ---
st.title("👤 Customer Details Lookup")

# Input for Customer ID
customer_id_input = st.text_input(
    "Enter Customer ID:", key="customer_id_input_detail", placeholder="e.g., 12345"
)  # Use unique key

# Button to fetch customer data
if st.button(
    "Get Customer Details", key="get_customer_button_detail"
):  # Use unique key
    if customer_id_input:
        try:
            # In a real app, you might have more robust error handling here
            # For now, we use the static method which returns dummy data based on the input ID
            customer_data = Customer.get_customer(customer_id_input)
            display_customer_details(customer_data)
            # Store fetched data in session state if needed for persistence across interactions on this page
            st.session_state["current_customer_details"] = customer_data
        except Exception as e:
            st.error(f"An error occurred while fetching customer data: {e}")
    else:
        st.error("Please enter a Customer ID.")

# Optional: Display details if already fetched and stored in session state (useful if page reloads)
# if 'current_customer_details' in st.session_state:
#    if not st.button("Clear Details"): # Add a clear button if using session state
#        display_customer_details(st.session_state['current_customer_details'])
#    else:
#        del st.session_state['current_customer_details']
#        st.rerun() # Rerun to clear the display
