import anvil.server
import anvil.secrets
import requests
import anvil.tables as tables
from anvil.tables import app_tables
import json

BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
COMPANY_ID = "9341452148700793"  # Replace with your QBO company ID

def get_qbo_access_token():
    """
    Retrieve the access token from the tokens data table. Automatically refreshes the token if not found.

    Returns:
        str: Access token.
    """
    # Try to get the access token from the data table
    token_row = app_tables.tokens.get(key="access_token")
    if token_row and token_row['value']:
        return token_row['value']

    # If not found or invalid, refresh the token
    print("Access token not found or expired. Refreshing...")
    return anvil.server.call('refresh_qbo_access_token_from_main_module')

@anvil.server.callable("refresh_qbo_access_token_from_main_module")
def refresh_qbo_access_token():
    """
    Refresh the QBO access token using the refresh token and store it in the data table.
    """
    client_id = anvil.secrets.get_secret("intuit_client_id")
    client_secret = anvil.secrets.get_secret("intuit_client_secret")
    refresh_token_row = app_tables.tokens.get(key="refresh_token")
    refresh_token = refresh_token_row['value'] if refresh_token_row else None

    if not refresh_token:
        raise Exception("Refresh token not found in the data table.")

    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    headers = {"Accept": "application/json"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()

    if "access_token" in response_data:
        # Update the access token in the data table
        app_tables.tokens.upsert({"key": "access_token", "value": response_data["access_token"]})

        # Update the refresh token if it changes
        if "refresh_token" in response_data:
            app_tables.tokens.upsert({"key": "refresh_token", "value": response_data["refresh_token"]})

        print("Access token refreshed successfully.")
        return response_data["access_token"]
    else:
        print(f"Failed to refresh access token: {response_data}")
        raise Exception(f"Failed to refresh access token: {response_data}")

@anvil.server.callable
def create_qbo_customer(first_name, last_name, email):
    """
    Create a customer in QuickBooks Online.

    Args:
        first_name (str): First name of the customer.
        last_name (str): Last name of the customer.
        email (str): Email address of the customer.

    Returns:
        dict: Customer details including the QBO customer ID.
    """
    # Validate inputs
    if not all([first_name, last_name, email]):
        raise ValueError("First name, last name, and email are required.")

    # Prepare the customer payload
    customer_payload = {
        "GivenName": first_name,
        "FamilyName": last_name,
        "PrimaryEmailAddr": {"Address": email}
    }

    try:
        access_token = get_qbo_access_token()
        url = f"{BASE_URL}{COMPANY_ID}/customer"

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
            new_token = refresh_qbo_access_token()
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
