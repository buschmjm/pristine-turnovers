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
      self.name_label.text = f"{customer['firstName']} {customer['lastName']}"
      self.email_label.text = customer['email']

  def select_customer_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
