import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from . import qboInvoices

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
  
  dropdown_items = []
  for item in items:
    formatted_item = {
      'display': f"{item['name']} - ${item['mattsCost']//100}.{item['mattsCost']%100:02d}",
      'value': dict(item)
    }
    dropdown_items.append(formatted_item)
    
  return dropdown_items

@anvil.server.callable
def format_qbo_invoice_data(bill_items, customer_info):
  """Format invoice data according to QBO API requirements"""
  qbo_line_items = []
  subtotal = 0
  tax_total = 0
  
  # Format regular line items without tax
  for item in bill_items:
    billing_item = item['billing_item']
    quantity = item['quantity']
    cost_per = billing_item['mattsCost']
    total_cost = cost_per * quantity
    tax = item.get('tax_amount', 0)
    
    # Calculate amounts for base price
    unit_price = cost_per / 100.0  # Convert cents to dollars
    line_amount = unit_price * quantity
    
    # Format line item without tax references
    qbo_line_item = {
      "DetailType": "SalesItemLineDetail",
      "Amount": line_amount,
      "Description": billing_item['name'],
      "SalesItemLineDetail": {
        "ItemRef": {
          "value": billing_item.get('qbo_item_id', '1'),
          "name": billing_item['name']
        },
        "UnitPrice": unit_price,
        "Qty": quantity
      }
    }
    qbo_line_items.append(qbo_line_item)
    subtotal += total_cost
    tax_total += tax

  # Add sales tax as separate line item if there is tax
  if tax_total > 0:
    tax_line_item = {
      "DetailType": "SalesItemLineDetail",
      "Amount": tax_total / 100.0,  # Convert cents to dollars
      "Description": "Sales Tax",
      "SalesItemLineDetail": {
        "ItemRef": {
          "value": "8",  # Use actual QBO Sales Tax item ID - you'll need to create this in QBO
          "name": "Sales Tax"
        },
        "UnitPrice": tax_total / 100.0,
        "Qty": 1
      }
    }
    qbo_line_items.append(tax_line_item)

  # Create invoice data
  invoice_data = {
    "Line": qbo_line_items,
    "CustomerRef": {
      "value": str(customer_info['qbId']),
      "name": f"{customer_info['firstName']} {customer_info['lastName']}"
    },
    "BillEmail": {
      "Address": customer_info['email']
    },
    "EmailStatus": "NeedToSend",
    "AllowOnlineCreditCardPayment": True,
    "AllowOnlineACHPayment": True
  }
  
  return invoice_data

@anvil.server.callable
def create_bill_with_items(bill_items, customer_info, existing_invoice_id=None):
  """Create or update bill and QBO invoice"""
  try:
    # Format and create/update QBO invoice
    invoice_data = format_qbo_invoice_data(bill_items, customer_info)
    
    if existing_invoice_id:
      existing_invoice = anvil.server.call('get_qbo_invoice', existing_invoice_id)
      invoice_data['Id'] = existing_invoice_id
      invoice_data['SyncToken'] = existing_invoice['SyncToken']
      qbo_invoice = anvil.server.call('update_qbo_invoice', invoice_data)
    else:
      qbo_invoice = anvil.server.call('create_qbo_invoice', invoice_data)

    # Save to local database
    bill = save_bill_to_database(bill_items, qbo_invoice, existing_invoice_id)
    
    return {
      'bill': bill,
      'qbo_invoice': qbo_invoice
    }
    
  except Exception as e:
    print(f"Error in create_bill_with_items: {str(e)}")  # Add logging
    raise ValueError(str(e))

def save_bill_to_database(bill_items, qbo_invoice, existing_invoice_id=None):
  """Save or update bill in local database"""
  try:
    # Calculate totals
    subtotal = sum(item['billing_item']['mattsCost'] * item['quantity'] for item in bill_items)
    tax_total = sum(item.get('tax_amount', 0) for item in bill_items)
    
    # Get QBO invoice ID safely
    invoice_id = qbo_invoice.get('Id') or qbo_invoice.get('id')
    if not invoice_id:
      raise ValueError("No invoice ID returned from QuickBooks")
    
    # Create billing items
    billing_item_rows = []
    for item in bill_items:
      item_row = app_tables.billing_items.add_row(
        itemName=item['billing_item']['name'],
        costPer=item['billing_item']['mattsCost'],
        quantity=item['quantity'],
        totalCost=item['billing_item']['mattsCost'] * item['quantity'],
        tax=item.get('tax_amount', 0)
      )
      billing_item_rows.append(item_row)

    # Update or create bill
    if existing_invoice_id:
      existing_bills = list(app_tables.bills.search(invoiceID=existing_invoice_id))
      if existing_bills:
        bill = existing_bills[0]
        bill.update(
          relatedItems=billing_item_rows,
          subtotal=subtotal,
          taxTotal=tax_total,
          grandTotal=subtotal + tax_total
        )
        return bill
        
    # Create new bill
    return app_tables.bills.add_row(
      relatedItems=billing_item_rows,
      subtotal=subtotal,
      taxTotal=tax_total,
      grandTotal=subtotal + tax_total,
      status='pending',
      createdAt=datetime.now(),
      captureStatus=False,
      invoiceID=invoice_id
    )
    
  except Exception as e:
    print(f"Database error detail: {str(e)}")  # More detailed error logging
    raise ValueError(f"Failed to save bill to database: {str(e)}")

# ... rest of existing billing library functions ...
