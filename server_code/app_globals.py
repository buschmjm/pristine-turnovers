import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_global_value(key):
  """Get a value from the globalvariables table"""
  row = app_tables.globalvariables.get(name=key)
  if row:
    return row['value']
  return None

@anvil.server.callable
def set_global_value(key, value):
  """Set a value in the globalvariables table"""
  row = app_tables.globalvariables.get(name=key)
  if row:
    row['value'] = value
    return value
  return None

@anvil.server.callable
def get_tax_rate():
  """Get tax rate from globalvariables"""
  tax_rate = get_global_value('tax')
  return float(tax_rate) if tax_rate is not None else 0.0

@anvil.server.callable
def update_tax_rate(new_rate):
  """Update tax rate in globalvariables"""
  rounded_rate = round(float(new_rate), 5)
  print(f"Updating tax rate to {rounded_rate}")
  return set_global_value('tax', rounded_rate)