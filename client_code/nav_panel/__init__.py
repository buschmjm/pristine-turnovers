from ._anvil_designer import nav_panelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class nav_panel(nav_panelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
  def collect_payment_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('collectPayment')

  def billing_library_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('billingLibrary')
