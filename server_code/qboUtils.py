import anvil.server
import anvil.secrets
import requests
from anvil.tables import app_tables

QBO_BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
QBO_COMPANY_ID = "9341452148700793"

def get_qbo_access_token():
    """Retrieve the access token from the tokens data table."""
    try:
        token_row = app_tables.tokens.get(key="intuit_access_token")
        if token_row and token_row['value']:
            return token_row['value']
        print("Access token not found or expired. Refreshing...")
        return anvil.server.call('refresh_qbo_access_token')
    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        raise Exception(f"Failed to get access token: {str(e)}")
