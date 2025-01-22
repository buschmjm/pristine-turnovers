import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_billing_items(show_active=True):
  return app_tables.billing_library.search(
    tables.order_by('name', ascending=True),
    active=show_active
  )

@anvil.server.callable
def create_billing_item():
  row = app_tables.billing_library.add_row(
    name='',
    mattsCost=0,
    cleanerCost=0,
    active=True,
    taxable=False
  )
  return row

@anvil.server.callable
def update_billing_item(item_id, name, matts_cost, cleaner_cost, taxable):
  row = app_tables.billing_library.get_by_id(item_id)
  if row:
    row.update(
      name=name,
      mattsCost=matts_cost,
      cleanerCost=cleaner_cost,
      taxable=taxable
    )
    return row

@anvil.server.callable
def set_billing_item_active(item_id, is_active):
  row = app_tables.billing_library.get_by_id(item_id)
  if row:
    row.update(active=is_active)

@anvil.server.callable
def delete_billing_item(item_id):
  row = app_tables.billing_library.get_by_id(item_id)
  if row:
    row.delete()

@anvil.server.callable
def get_active_billing_items_for_dropdown():
  """Get all active billing items formatted for dropdown"""
  return app_tables.billing_library.search(
    active=True,
    tables.order_by('name')
  )
