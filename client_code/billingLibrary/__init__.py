from ._anvil_designer import billingLibraryTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

class billingLibrary(billingLibraryTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    
    # Style the action buttons
    self.add_item_button.background = '#4CAF50'  # Material green
    self.add_item_button.foreground = 'white'
    self.add_item_button.font_size = 16
    self.add_item_button.role = 'raised'
    
    self.view_inactive_button.background = '#FF9800'  # Material orange
    self.view_inactive_button.foreground = 'white'
    self.view_inactive_button.font_size = 16
    self.view_inactive_button.role = 'raised'
    
    # Style the grid
    self.billing_items_grid.bold_headers = True
    self.billing_items_grid.background = '#FFFFFF'
    self.billing_items_grid.border = '1px solid #E0E0E0'
    
    self.show_active = True
    self.refresh_grid()
    
  def refresh_grid(self):
    # Pull items from server
    items = anvil.server.call('get_billing_items', self.show_active)
    self.items_repeating_panel.items = items
    
    # Update button text
    self.view_inactive_button.text = (
      "View Active" if not self.show_active else "View Inactive"
    )

  def add_item_button_click(self, **event_args):
    new_row = anvil.server.call('create_billing_item')
    self.refresh_grid()
    
    # Then find and edit the new row
    for c in self.items_repeating_panel.get_components():
      if c.item == new_row:
        c.enable_edit_mode()
        break

  def view_inactive_button_click(self, **event_args):
    self.show_active = not self.show_active
    self.refresh_grid()
