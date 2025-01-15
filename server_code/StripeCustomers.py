import anvil.server
import anvil.secrets
import requests
import json


BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
COMPANY_ID = "9341452148700793"  # Replace with your QBO company ID
HARDCODED_CUSTOMER_ID = "1"  # Replace this with the actual customer ID you're using for testing

def get_qbo_access_token():
    """
    Retrieve the access token directly from Anvil Secrets.

    Returns:
        str: Access token.
    """
    access_token = anvil.secrets.get_secret("intuit_access_token")  # Stored manually in Secrets
    if not access_token:
        raise Exception("Access token is not set. Generate it manually and add it to Secrets.")
    return access_token

@anvil.server.callable
def create_qbo_invoice(line_items):
    """
    Create an invoice in QuickBooks Online with a hardcoded customer ID.

    Args:
        line_items (list): List of dictionaries, each containing 'description', 'amount', and 'quantity'.

    Returns:
        dict: Response from QBO API, including the invoice ID if successful.
    """
    # Validate input
    if not isinstance(line_items, list) or len(line_items) == 0:
        raise ValueError("Invalid input: 'line_items' must be a non-empty list.")

    # Use the hardcoded customer ID
    customer_id = HARDCODED_CUSTOMER_ID

    # Get access token
    access_token = get_qbo_access_token()
    url = f"{BASE_URL}{COMPANY_ID}/invoice"

    # Prepare the invoice payload
    invoice_payload = {
        "CustomerRef": {"value": customer_id},
        "Line": [
            {
                "DetailType": "SalesItemLineDetail",
                "Amount": item["amount"] * item["quantity"],
                "SalesItemLineDetail": {
                    "ItemRef": {"value": item["item_id"]},  # Replace with appropriate item ID
                    "Qty": item["quantity"]
                },
                "Description": item["description"]
            }
            for item in line_items
        ]
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(invoice_payload))
    response_data = response.json()

    # Handle the response
    if response.status_code == 200 and "Invoice" in response_data and "Id" in response_data["Invoice"]:
        invoice_id = response_data["Invoice"]["Id"]
        print(f"Invoice created successfully. ID: {invoice_id}")
        return response_data["Invoice"]
    else:
        # Log and raise an exception if the response is invalid
        print(f"Failed to create invoice. Response: {response_data}")
        raise Exception(f"Failed to create invoice: {response_data}")
