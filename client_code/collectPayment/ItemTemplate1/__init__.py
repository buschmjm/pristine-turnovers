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
    customers = anvil.server.call(
      "customerQueries",
      email=None,
      startDate=None,
      endDate=None,
      firstName=None,
      lastName=None
      )
    self.repeating_panel_1.items = [
        {'name': customer['firstName'], 'email': customer['email']} for customer in customers
      ]

    # Any code you write here will run before the form opens.
