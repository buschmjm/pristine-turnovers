from ._anvil_designer import ItemTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate1(ItemTemplate1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    if 'item' in properties:
      customer = properties['item']
      print(f"Loading customer: {customer['firstName']} {customer['lastName']}")
      
      # Set customer name and email only, remove QB ID display
      name = f"{customer['firstName']} {customer['lastName']}"
      email = customer.get('email', 'No email')
      
      self.name_label.text = name
      self.email_label.text = email
      
      # Optional: Add QB ID status to name if you want to show it
      # has_qb = 'qbId' in customer and customer['qbId']
      # self.name_label.text = f"{name} {'✓' if has_qb else ''}"

  def select_customer_button_click(self, **event_args):
    customer = self.item
    print(f"Selected customer: {customer['firstName']} {customer['lastName']}")
    get_open_form().select_customer(customer, self)
