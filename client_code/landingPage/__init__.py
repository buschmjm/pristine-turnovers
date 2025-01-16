from ._anvil_designer import landingPageTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil

class landingPage(landingPageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Pre-warm the server connection
    anvil.server.call("customerQueries")

    # Any code you write here will run before the form opens.

  def create_invoice_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def collect_payment_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('collectPayment')
