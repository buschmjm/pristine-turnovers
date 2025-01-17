from ._anvil_designer import billingLibraryTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class billingLibrary(billingLibraryTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def add_item_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def view_inactive_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
