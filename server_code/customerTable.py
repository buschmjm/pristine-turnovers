import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def customerQueries(email=None, startDate=None, endDate=None, firstName=None, lastName=None):
    # Prepare keyword arguments for the search query
    search_kwargs = {}
    
    # Add conditions only if variables are not empty
    if email:
        search_kwargs['email'] = email
    if firstName:
        search_kwargs['firstName'] = firstName
    if lastName:
        search_kwargs['lastName'] = lastName
    if startDate and endDate:
        search_kwargs['date'] = q.between(startDate, endDate, min_inclusive=True, max_inclusive=True)

    # Execute the search with the prepared keyword arguments
    query = app_tables.customers.search(**search_kwargs)

    return list(query)