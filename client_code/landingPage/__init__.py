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
    self.init_components(**properties)
    
    # Style the main navigation buttons
    for button in [self.collect_payment_button, self.billing_library_button]:
      button.background = '#1976D2'  # Material Design primary blue
      button.foreground = 'white'
      button.font_size = 18
      button.font = 'Roboto'
      button.role = 'raised'
      button.border = '0px'

    # Pre-warm the server connection
    anvil.server.call("customerQueries")

    # Any code you write here will run before the form opens.

  def collect_payment_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('collectPayment')

  def billing_library_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('billingLibrary')
