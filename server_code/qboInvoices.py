import anvil.server
import requests
from . import qboUtils
from datetime import datetime

@anvil.server.callable
def get_qbo_invoice(invoice_id):
  """Get invoice details from QBO"""
  access_token = qboUtils.get_qbo_access_token()
  url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/invoice/{invoice_id}"
  
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
  }
  
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    return response.json()['Invoice']
  raise Exception(f"Failed to get invoice: {response.text}")

@anvil.server.callable
def create_qbo_invoice(invoice_data):
  """Create a new invoice in QBO"""
  access_token = qboUtils.get_qbo_access_token()
  url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/invoice"
  
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }
  
  response = requests.post(url, headers=headers, json=invoice_data)
  if response.status_code == 200:
    return response.json()['Invoice']
  raise Exception(f"Failed to create invoice: {response.text}")

@anvil.server.callable
def update_qbo_invoice(invoice_data):
  """Update an existing invoice in QBO"""
  if not invoice_data.get('Id') or not invoice_data.get('SyncToken'):
    raise ValueError("Invoice ID and SyncToken are required for updates")
    
  access_token = qboUtils.get_qbo_access_token()
  url = f"{qboUtils.QBO_BASE_URL}{qboUtils.QBO_COMPANY_ID}/invoice"
  
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
  }
  
  response = requests.post(url, headers=headers, json=invoice_data)
  if response.status_code == 200:
    return response.json()['Invoice']
  raise Exception(f"Failed to update invoice: {response.text}")
