import anvil.server
import requests
import json
from anvil.tables import app_tables
from . import qboUtils
from . import accessRenewal
from datetime import datetime  # This is all we need

@anvil.server.callable
def check_existing_customer(email):
    """Check if a customer already exists in QBO by email."""
    try:
        access_token = qboUtils.get_qbo_access_token()
        url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/query"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Query for customer with matching email
        query = f"select * from Customer where PrimaryEmailAddr = '{email}'"
        response = requests.get(f"{url}?query={query}", headers=headers)
        data = response.json()
        
        if "QueryResponse" in data and "Customer" in data["QueryResponse"]:
            return data["QueryResponse"]["Customer"][0]
        return None
    except Exception as e:
        print(f"Error checking existing customer: {e}")
        raise

@anvil.server.callable
def create_and_store_customer(first_name, last_name, email):
    """Create customer in QBO and store in local table."""
    # First check if customer exists
    existing_customer = check_existing_customer(email)
    if existing_customer:
        raise Exception("Customer with this email already exists in QuickBooks Online")
        
    # Create customer in QBO
    qbo_customer = create_qbo_customer(first_name, last_name, email)
    
    # Store in local table with current timestamp
    try:
        customer_row = app_tables.customers.add_row(
            stripeId=qbo_customer["Id"],
            firstName=first_name,
            lastName=last_name,
            email=email,
            lastAccessed=datetime.now()  # Anvil will handle the timezone automatically
        )
        
        return {
            "success": True,
            "customerId": qbo_customer["Id"],
            "customerData": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "created": datetime.now()
            }
        }
    except Exception as e:
        print(f"Error storing customer in local table: {e}")
        raise Exception("Customer created in QBO but failed to store locally")

@anvil.server.callable
def create_qbo_customer(first_name, last_name, email):
    """Create a customer in QuickBooks Online with date prefix to handle duplicate names."""
    if not all([first_name, last_name, email]):
        raise ValueError("First name, last name, and email are required.")

    # Add date prefix in mm/dd/yy format
    date_prefix = datetime.now().strftime("%m/%d/%y")
    
    customer_payload = {
        "Title": date_prefix,  # Add date as prefix/title
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
