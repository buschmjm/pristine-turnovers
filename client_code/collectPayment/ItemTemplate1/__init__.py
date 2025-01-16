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
      # Update these lines to match your actual label component names
      # For example, if your labels are named 'label_1' and 'label_2':
      self.label_1.text = f"{customer['firstName']} {customer['lastName']}"
      self.label_2.text = customer['email']
