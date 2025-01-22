import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_global_value(key):
  """Get a value from the globalvariables table"""
  row = app_tables.globalvariables.get(tax=key)  # Changed to use 'tax' column directly
  if row:
    return row['value']
  return None

@anvil.server.callable
def set_global_value(key, value):
  """Set a value in the globalvariables table"""
  row = app_tables.globalvariables.get(variable=key)  # Changed from 'name' to 'variable'
  if row:
    row['value'] = value
    return value
  return None

@anvil.server.callable
def get_tax_rate():
  """Get tax rate from globalvariables"""
  row = app_tables.globalvariables.get()  # Get the single row
  if row:
    return float(row['tax'])  # Get tax value directly
  return 0.0

@anvil.server.callable
def update_tax_rate(new_rate):
  """Update tax rate in globalvariables"""
  rounded_rate = round(float(new_rate), 5)
  print(f"Updating tax rate to {rounded_rate}")
  row = app_tables.globalvariables.get()  # Get the single row
  if row:
    row['tax'] = rounded_rate  # Update tax directly
  return rounded_rate