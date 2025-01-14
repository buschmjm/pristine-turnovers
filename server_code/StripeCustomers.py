import anvil.secrets
import anvil.users
import anvil.tables as tables 
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import datetime
import time
import StripeCustomers

@anvil.server.background_task
def get_recent_customers():
    # Retrieve the Stripe secret key from Anvil's secrets
    stripe_secret_key = anvil.secrets.get_secret("pristine_stripe_test_secret")

    # Calculate the Unix timestamp for six months ago
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=182)
    six_months_ago_timestamp = int(time.mktime(six_months_ago.timetuple()))

    # Set up the request to Stripe's API
    url = 'https://api.stripe.com/v1/customers'
    headers = {
        'Authorization': f'Bearer {stripe_secret_key}'
    }
    params = {
        'created[gte]': six_months_ago_timestamp,
        'limit': 100  # Adjust the limit as needed; max is 100
    }

    customers = []
    has_more = True
    starting_after = None

    while has_more:
        if starting_after:
            params['starting_after'] = starting_after

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()
        customers.extend(data['data'])
        has_more = data.get('has_more', False)
        if has_more:
            starting_after = data['data'][-1]['id']

    return customers