import anvil.server
from . import qboUtils

@anvil.server.callable
def create_qbo_invoice(invoice_data):
  """Create a new invoice in QBO"""
  try:
    response = qboUtils.make_qbo_request('POST', 'invoice', data=invoice_data)
    if 'Invoice' in response:
      return response['Invoice']
    raise ValueError("No invoice data in QBO response")
  except Exception as e:
    print(f"QBO invoice creation error: {str(e)}")
    raise

@anvil.server.callable
def get_qbo_invoice(invoice_id):
    """Get invoice details from QBO"""
    try:
        return qboUtils.make_qbo_request('GET', f'invoice/{invoice_id}')
    except Exception as e:
        print(f"Failed to get invoice: {str(e)}")
        raise

@anvil.server.callable
def update_qbo_invoice(invoice_data):
    """Update an existing invoice in QBO"""
    try:
        if not invoice_data.get('Id') or not invoice_data.get('SyncToken'):
            raise ValueError("Invoice ID and SyncToken are required for updates")
        return qboUtils.make_qbo_request('POST', 'invoice', data=invoice_data)
    except Exception as e:
        print(f"Failed to update invoice: {str(e)}")
        raise
