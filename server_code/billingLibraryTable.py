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
  """Get active billing items formatted for dropdown"""
  items = app_tables.billing_library.search(
    tables.order_by('name'),
    active=True
  )
  print(f"Found {len(items)} active items")  # Debug print
  
  dropdown_items = []
  for item in items:
    formatted_item = {
      'display': f"{item['name']} - ${item['mattsCost']//100}.{item['mattsCost']%100:02d}",
      'value': dict(item)
    }
    print(f"Formatted item: {formatted_item['display']}")  # Debug print
    dropdown_items.append(formatted_item)
    
  return dropdown_items

@anvil.server.callable
def create_bill_with_items(bill_items, customer_info):
  """Create a new bill and its associated items"""
  # First create all billing items
  billing_item_rows = []
  subtotal = 0
  tax_total = 0
  
  for item in bill_items:
    billing_item = item['billing_item']
    quantity = item['quantity']
    cost_per = billing_item['mattsCost']
    total_cost = cost_per * quantity
    tax = item.get('tax_amount', 0)
    
    # Create billing item row
    item_row = app_tables.billing_items.add_row(
      itemName=billing_item['name'],
      costPer=cost_per,
      quantity=quantity,
      totalCost=total_cost,
      tax=tax
    )
    billing_item_rows.append(item_row)
    subtotal += total_cost
    tax_total += tax

  # Create QBO invoice
  line_items = [{
    "item_id": item['billing_item'].get('qbo_item_id'),
    "description": item['billing_item']['name'],
    "amount": item['billing_item']['mattsCost'] / 100.0,  # Convert cents to dollars
    "quantity": item['quantity']
  } for item in bill_items]
  
  qbo_invoice = anvil.server.call('create_qbo_invoice', line_items, customer_info)
  
  # Create bill record
  bill = app_tables.bills.add_row(
    relatedItems=billing_item_rows,
    subtotal=subtotal,
    taxTotal=tax_total,
    grandTotal=subtotal + tax_total,
    status='pending',
    createdAt=datetime.now(),
    captureStatus=False,
    invoiceID=qbo_invoice['Id']
  )
  
  return {
    'bill': bill,
    'qbo_invoice': qbo_invoice
  }
