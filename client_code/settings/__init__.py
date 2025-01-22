from ._anvil_designer import settingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class settings(settingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def edit_tax_rate_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def save_tax_rate_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def tax_percentage_text_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass
