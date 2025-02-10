from ._anvil_designer import nav_panelTemplate
from anvil import *

class nav_panel(nav_panelTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        # Remove duplicate button if it exists
        if hasattr(self, 'existing_bills_button_2'):
            self.existing_bills_button_2.remove_from_parent()

    # ...existing code...
