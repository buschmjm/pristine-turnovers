import anvil.server
import requests
from anvil.tables import app_tables

@anvil.server.callable
def refresh_qbo_access_token():
    """Refresh the QBO access token using the refresh token."""
    client_id = anvil.secrets.get_secret("intuit_client_id")
    client_secret = anvil.secrets.get_secret("intuit_client_secret")
    
    refresh_token_row = app_tables.tokens.get(key="intuit_refresh_token")
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
        # Update token handling with proper row creation
        try:
            # Try to get existing row first
            access_token_row = app_tables.tokens.get(key="intuit_access_token")
            if access_token_row:
                access_token_row['value'] = response_data["access_token"]
            else:
                app_tables.tokens.add_row(key="intuit_access_token", value=response_data["access_token"])

            # Handle refresh token the same way
            if "refresh_token" in response_data:
                refresh_token_row = app_tables.tokens.get(key="intuit_refresh_token")
                if refresh_token_row:
                    refresh_token_row['value'] = response_data["refresh_token"]
                else:
                    app_tables.tokens.add_row(key="intuit_refresh_token", value=response_data["refresh_token"])

            print("Access token refreshed successfully.")
            return response_data["access_token"]
        except Exception as e:
            print(f"Error updating tokens: {str(e)}")
            raise Exception(f"Failed to update tokens: {str(e)}")
    else:
        print(f"Failed to refresh access token: {response_data}")
        raise Exception(f"Failed to refresh access token: {response_data}")

def get_qbo_access_token():
    """
    Retrieve the access token from the tokens data table. Automatically refreshes the token if not found.

    Returns:
        str: Access token.
    """
    token_row = app_tables.tokens.get(key="intuit_access_token")
    if token_row and token_row['value']:
        return token_row['value']

    print("Access token not found or expired. Refreshing...")
    return anvil.server.call('refresh_qbo_access_token')
