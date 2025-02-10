import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

@anvil.server.callable
def get_customers():
    """Get all customers with minimal logging"""
    try:
        customers = app_tables.customers.search(
            tables.order_by("lastName", ascending=True)
        )
        return [{
            'id': c['qbId'],
            'firstName': c['firstName'],
            'lastName': c['lastName'],
            'email': c['email']
        } for c in customers]
    except Exception as e:
        print(f"Error fetching customers: {str(e)}")
        return []
