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
        # Get all customers, sorted by last name
        customers = list(app_tables.customers.search(
            tables.order_by("lastName", ascending=True)
        ))
        print(f"Found {len(customers)} customers")  # Debug print

        # Convert each customer to a dictionary to avoid LiveObjectProxy issues
        formatted_customers = []
        for customer in customers:
            # Handle missing fields safely
            qb_id = None
            try:
                qb_id = customer['qbId']
            except KeyError:
                pass
                
            last_accessed = None
            try:
                last_accessed = customer['lastAccessed']
            except KeyError:
                pass
                
            customer_dict = {
                'firstName': customer['firstName'],
                'lastName': customer['lastName'],
                'email': customer['email'],
                'qbId': qb_id,
                'lastAccessed': last_accessed
            }
            formatted_customers.append(customer_dict)
            print(f"Loaded customer: {customer_dict['firstName']} {customer_dict['lastName']}")

        return formatted_customers

    except Exception as e:
        print(f"Error in customerQueries: {str(e)}")  # Debug print
        return []

@anvil.server.callable
def ensure_customer_qbo_id(customer):
    """Ensure customer has QBO ID, return True if successful"""
    try:
        # Check for qbId using direct attribute access
        has_qb_id = False
        try:
            has_qb_id = bool(customer['qbId'])
        except KeyError:
            pass
            
        if not has_qb_id:
            qbCustomers.sync_customer_with_qbo(customer)
        return True
        
    except Exception as e:
        print(f"Failed to ensure QBO ID: {str(e)}")
        return False