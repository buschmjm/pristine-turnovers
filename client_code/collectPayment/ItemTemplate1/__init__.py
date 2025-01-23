from ._anvil_designer import ItemTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate1(ItemTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Get the item data from the properties passed to this template
    if 'item' in properties:
      customer = properties['item']
      print(f"Loading customer: {customer['firstName']} {customer['lastName']}")  # Debug print
      
      # Handle potentially missing fields safely
      email = "No email"
      try:
          email = customer['email']
      except KeyError:
          pass
          
      qb_id = "Not synced"
      try:
          qb_id = customer['qbId']
      except KeyError:
          pass
          
      self.name_label.text = f"{customer['firstName']} {customer['lastName']}"
      self.email_label.text = email
      self.qb_id_label.text = f"QB ID: {qb_id}"

  def select_customer_button_click(self, **event_args):
    """Handle customer selection"""
    customer = self.item  # Get the customer data from this template's item
    print(f"Selected customer: {customer['firstName']} {customer['lastName']}")  # Debug print
    get_open_form().select_customer(customer, self)  # Call parent form's selection handler
