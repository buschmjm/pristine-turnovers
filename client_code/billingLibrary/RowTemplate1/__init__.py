from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def deactivate_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def edit_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def activate_row_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
