import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def customerQueries(email=None, startDate=None, endDate=None, firstName=None, lastName=None):
    print("Starting customer query...")  # Debug print
    try:
        customers = list(app_tables.customers.search())
        print(f"Found {len(customers)} customers")  # Debug print
        return customers
    except Exception as e:
        print(f"Error in customerQueries: {str(e)}")  # Debug print
        return []