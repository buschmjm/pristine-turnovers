import anvil.server
import requests
import json
from anvil.tables import app_tables
from . import qboUtils
from . import accessRenewal

@anvil.server.callable
def create_and_store_customer(first_name, last_name, email):
    """Create customer in QBO and store in local table."""
    # First create the customer in QBO
    qbo_customer = create_qbo_customer(first_name, last_name, email)
    
    # Then store in local table
    try:
        app_tables.customers.add_row(
            stripeId=qbo_customer["Id"],
            firstName=first_name,
            lastName=first_name,
            email=email
        )
        return qbo_customer
    except Exception as e:
        print(f"Error storing customer in local table: {e}")
        raise Exception("Customer created in QBO but failed to store locally")

@anvil.server.callable
def create_qbo_customer(first_name, last_name, email):
    """Create a customer in QuickBooks Online."""
    if not all([first_name, last_name, email]):
        raise ValueError("First name, last name, and email are required.")

    customer_payload = {
        "GivenName": first_name,
        "FamilyName": last_name,
        "PrimaryEmailAddr": {"Address": email}
    }

    try:
        access_token = qboUtils.get_qbo_access_token()
        url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/customer"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, data=json.dumps(customer_payload))
        response_data = response.json()

        if response.status_code == 200 and "Customer" in response_data:
            customer_id = response_data["Customer"]["Id"]
            print(f"Customer created successfully. ID: {customer_id}")
            return response_data["Customer"]
        else:
            # Handle token expiration and retry
            print("Initial request failed, refreshing token and retrying...")
            new_token = accessRenewal.refresh_qbo_access_token()
            headers["Authorization"] = f"Bearer {new_token}"
            response = requests.post(url, headers=headers, data=json.dumps(customer_payload))
            response_data = response.json()

            if response.status_code == 200 and "Customer" in response_data:
                customer_id = response_data["Customer"]["Id"]
                print(f"Customer created successfully after token refresh. ID: {customer_id}")
                return response_data["Customer"]
            else:
                raise Exception(f"Failed to create customer after token refresh: {response_data}")
    except Exception as e:
        print(f"Error creating customer: {e}")
        raise
