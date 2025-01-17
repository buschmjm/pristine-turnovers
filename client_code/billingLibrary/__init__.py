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
    self.show_active = True
    self.refresh_grid()
    
  def refresh_grid(self):
    # Proper Anvil query syntax using q.fetch()
    query = q.fetch(app_tables.billing_items)
    query = query.where(q.prop('active') == self.show_active)
    query = query.sort('name')
    self.items_repeating_panel.items = query
    
    # Update button visibility based on active/inactive view
    self.view_inactive_button.text = "View Active" if not self.show_active else "View Inactive"

  def add_item_button_click(self, **event_args):
    # Add new empty row and open in edit mode
    new_row = app_tables.billing_items.add_row(
      name='', mattsCost=0, cleanerCost=0, active=True
    )
    self.refresh_grid()
    # Find the new template and put it in edit mode
    for c in self.items_repeating_panel.get_components():
      if c.item == new_row:
        c.enable_edit_mode()
        break

  def view_inactive_button_click(self, **event_args):
    self.show_active = not self.show_active
    self.refresh_grid()
