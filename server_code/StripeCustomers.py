import anvil.stripe
import anvil.secrets
import anvil.users
import anvil.tables as tables 
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import datetime
import time


# Initialize Stripe with your secret key
anvil.stripe.api_key = anvil.secrets.get_secret('pristine_stripe_test_secret')

@anvil.server.callable
def get_billing_items():
    try:
        # Fetch billing items (e.g., products, prices, etc.)
        prices = anvil.stripe.Price.list(limit=100)  # Adjust limit as needed
        billing_items = [{'description': price['product'], 'amount': price['unit_amount']} for price in prices['data']]
        return billing_items
    except Exception as e:
        raise anvil.server.AnvilWrappedError(f"Error retrieving billing items: {e}")

@anvil.server.callable
def add_customer(id, name, email, company):
  app_tables.articles.add_row(
      stripeId=id,
      name=name,
      email=email,
      company=company
  )