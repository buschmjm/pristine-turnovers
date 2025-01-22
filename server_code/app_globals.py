import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

TAX_RATE = 0.10375

@anvil.server.callable
def get_tax_rate():
  return TAX_RATE

@anvil.server.callable
def update_tax_rate(new_rate):
  global TAX_RATE
  print(f"Updating tax rate from {TAX_RATE} to {new_rate}")  # Debug print
  TAX_RATE = round(float(new_rate), 5)  # Round to 5 decimal places
  print(f"New tax rate set to: {TAX_RATE}")  # Debug print
  return TAX_RATE