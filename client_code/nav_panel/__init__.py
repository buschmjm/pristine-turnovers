from ._anvil_designer import nav_panelTemplate
from anvil import *

class nav_panel(nav_panelTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.remove_duplicate_buttons()
        
    def remove_duplicate_buttons(self):
        """Remove any duplicate buttons from the panel"""
        # Get all components with the name 'existing_bills_button'
        buttons = [comp for comp in self.get_components() 
                  if hasattr(comp, 'name') and comp.name == 'existing_bills_button']
        
        # Keep only the first one, remove others
        if len(buttons) > 1:
            for button in buttons[1:]:
                button.remove_from_parent()

    # ...existing code...
