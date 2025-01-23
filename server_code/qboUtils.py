import anvil.server
import anvil.secrets
import requests
from anvil.tables import app_tables
from . import accessRenewal

QBO_BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
QBO_COMPANY_ID = "9341452148700793"

def get_qbo_access_token(force_refresh=False):
    """Get QBO access token with auto-refresh"""
    try:
        if not force_refresh:
            token_row = app_tables.tokens.get(key="intuit_access_token")
            if token_row and token_row['value']:
                return token_row['value']
                
        print("Getting fresh access token...")
        new_token = accessRenewal.refresh_qbo_access_token()
        return new_token
        
    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        raise Exception(f"Failed to get access token: {str(e)}")

def make_qbo_request(method, endpoint, data=None, retry=True):
    """Make a request to QBO API with token refresh handling"""
    try:
        url = f"{QBO_BASE_URL}{QBO_COMPANY_ID}/{endpoint}"
        access_token = get_qbo_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        # Handle 401 with retry
        if response.status_code == 401 and retry:
            print("Token expired, refreshing...")
            access_token = get_qbo_access_token(force_refresh=True)
            headers["Authorization"] = f"Bearer {access_token}"
            return make_qbo_request(method, endpoint, data, retry=False)
            
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {str(e)}")
        print(f"Response: {e.response.text}")
        raise Exception(f"QBO API Error: {e.response.text}")
    except Exception as e:
        print(f"Error making QBO request: {str(e)}")
        raise
