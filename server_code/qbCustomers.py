import anvil.server
import requests
import json
from anvil.tables import app_tables
from . import qboUtils
from . import accessRenewal
from datetime import datetime, timedelta

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
            qbId=qbo_customer["Id"],  # Changed from stripeId to qbId
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
    """Create a customer in QuickBooks Online."""
    if not all([first_name, last_name, email]):
        raise ValueError("First name, last name, and email are required.")

    # First attempt without date prefix
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
            # Check if it's a duplicate name error
            if ("Fault" in response_data and 
                response_data["Fault"]["Error"][0].get("code") == "6240" and 
                "Duplicate Name Exists Error" in response_data["Fault"]["Error"][0].get("Message", "")):
                
                print("Duplicate name detected, retrying with creation date as title...")
                # Add date prefix and retry
                date_prefix = datetime.now().strftime("%m/%d/%y")
                customer_payload["Title"] = date_prefix

                # Try again with date prefix
                response = requests.post(url, headers=headers, data=json.dumps(customer_payload))
                response_data = response.json()

                if response.status_code == 200 and "Customer" in response_data:
                    customer_id = response_data["Customer"]["Id"]
                    print(f"Customer created successfully with date prefix. ID: {customer_id}")
                    return response_data["Customer"]
            
            # If we get here, either it wasn't a duplicate name error or the retry failed
            # Handle token expiration and retry one last time
            print("Request failed, refreshing token and retrying...")
            new_token = accessRenewal.refresh_qbo_access_token()
            headers["Authorization"] = f"Bearer {new_token}"
            response = requests.post(url, headers=headers, data=json.dumps(customer_payload))
            response_data = response.json()

            if response.status_code == 200 and "Customer" in response_data:
                customer_id = response_data["Customer"]["Id"]
                print(f"Customer created successfully after token refresh. ID: {customer_id}")
                return response_data["Customer"]
            else:
                # Final error handling
                if "Fault" in response_data:
                    error_code = response_data["Fault"]["Error"][0].get("code", "")
                    error_message = response_data["Fault"]["Error"][0].get("Message", "")
                    error_detail = response_data["Fault"]["Error"][0].get("Detail", "")
                    
                    if error_code == "6240" and "Duplicate Name Exists Error" in error_message:
                        raise Exception("A customer with this name already exists in QuickBooks Online. "
                                     "This can happen if another customer was created on the same date. "
                                     "Please try again tomorrow or contact support if this is urgent.")
                    else:
                        raise Exception(f"QuickBooks Error: {error_message} - {error_detail}")
                else:
                    raise Exception(f"Failed to create customer: {response_data}")
    except Exception as e:
        print(f"Error creating customer: {e}")
        raise

@anvil.server.callable
def get_recent_customers(months_active=3):
    """Get customers who were active within the specified number of months."""
    cutoff_date = datetime.now() - timedelta(days=months_active * 30)
    
    try:
        recent_customers = app_tables.customers.search(
            tables.order_by("lastName", ascending=True),
            lastAccessed=q.greater_than(cutoff_date)
        )
        
        # Format customers for dropdown
        return [{
            'value': str(c['qbId']),  # Ensure value is string
            'text': f"{c['firstName']} {c['lastName']} ({c['email']})"
        } for c in recent_customers]
    except Exception as e:
        print(f"Error fetching recent customers: {e}")
        raise

@anvil.server.callable
def find_qbo_customer_by_email(email):
    """Find a customer in QBO by email address"""
    try:
        access_token = qboUtils.get_qbo_access_token()
        url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/query"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        query = f"select * from Customer where PrimaryEmailAddr = '{email}'"
        response = requests.get(f"{url}?query={query}", headers=headers)
        data = response.json()
        
        if "QueryResponse" in data and "Customer" in data["QueryResponse"]:
            return data["QueryResponse"]["Customer"][0]
        return None
        
    except Exception as e:
        print(f"Error finding QBO customer: {str(e)}")
        return None

@anvil.server.callable
def sync_customer_with_qbo(customer_row):
    """Sync customer record with QBO - find or create"""
    try:
        # First try to find in QBO by email
        qbo_customer = find_qbo_customer_by_email(customer_row['email'])
        
        if qbo_customer:
            # Update local record with QBO ID
            customer_row.update(qbId=qbo_customer['Id'])
            return qbo_customer['Id']
            
        # If not found, create new QBO customer
        new_qbo_customer = create_qbo_customer(
            customer_row['firstName'],
            customer_row['lastName'],
            customer_row['email']
        )
        
        # Update local record with new QBO ID
        customer_row.update(qbId=new_qbo_customer['Id'])
        return new_qbo_customer['Id']
        
    except Exception as e:
        print(f"Error syncing customer with QBO: {str(e)}")
        raise
