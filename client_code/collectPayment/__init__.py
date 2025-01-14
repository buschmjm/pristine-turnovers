from ._anvil_designer import collectPaymentTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class collectPayment(collectPaymentTemplate):
    def __init__(self, **properties):
      # Set Form properties and Data Bindings.
      self.init_components(**properties)
      # Any code you write here will run before the form opens.   

    def customer_selector_show(self, **event_args):
      try:
        customers = anvil.server.call('get_recent_customers')
        self.customer_selector.items = customers
      except anvil.server.AnvilWrappedError as e:
        alert(f"Failed to retrieve Customers: {e}")
      pass
  