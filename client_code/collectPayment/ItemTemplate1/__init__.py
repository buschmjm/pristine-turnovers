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
      self.customer = properties['item']
      self.name_label.text = f"{self.customer['firstName']} {self.customer['lastName']}"
      self.email_label.text = self.customer['email']
