from ._anvil_designer import landingPageTemplate
from anvil import *


class landingPage(landingPageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def create_invoice_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def collect_payment_button_click(self, **event_args):
    """This met\hod is called when the button is clicked"""
    pass
