import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import qbCustomers

@anvil.server.callable
def customerQueries(email=None, startDate=None, endDate=None, firstName=None, lastName=None):
    print("Starting customer query...")  # Debug print
    try:
        customers = list(app_tables.customers.search())
        print(f"Found {len(customers)} customers")  # Debug print
        
        # Check for missing QBO IDs and try to sync
        for customer in customers:
            if not customer.get('qbId'):
                try:
                    qbCustomers.sync_customer_with_qbo(customer)
                except Exception as e:
                    print(f"Failed to sync customer {customer['email']}: {str(e)}")
                    
        return customers
    except Exception as e:
        print(f"Error in customerQueries: {str(e)}")  # Debug print
        return []

@anvil.server.callable
def ensure_customer_qbo_id(customer):
    """Ensure customer has QBO ID, return True if successful"""
    try:
        if not customer.get('qbId'):
            qbCustomers.sync_customer_with_qbo(customer)
        return True
    except Exception as e:
        print(f"Failed to ensure QBO ID: {str(e)}")
        return False