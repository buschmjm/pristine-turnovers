from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.update_display()
    # Set initial button visibility
    self.edit_row.visible = True
    self.save_row.visible = False
    self.cancel_edit.visible = False
    
    # Add tooltips to buttons
    self.edit_row.tooltip = "Edit this item"
    self.save_row.tooltip = "Save changes"
    self.cancel_edit.tooltip = "Cancel changes"
    self.activate_row.tooltip = "Make item active"
    self.deactivate_row.tooltip = "Make item inactive"
    
  def update_display(self):
    name = self.item['name']
    matts_pennies = self.item['mattsCost'] or 0
    cleaner_pennies = self.item['cleanerCost'] or 0
    
    # Add taxable display
    self.taxable_label.text = "Yes" if self.item['taxable'] else "No"

    # Convert pennies to dollars string (e.g., 199 pennies -> "$1.99")
    self.name_label.text = name
    self.matts_cost_label.text = f"${matts_pennies//100}.{matts_pennies%100:02d}"
    self.cleaner_cost_label.text = f"${cleaner_pennies//100}.{cleaner_pennies%100:02d}"
    
    # Set initial visibility
    self.set_edit_mode(False)
    self.activate_row.visible = not self.item['active']
    self.deactivate_row.visible = self.item['active']
    
  def set_edit_mode(self, editing):
    # Toggle visibility of edit components
    self.name_text_box.visible = editing
    self.matts_cost_text_box.visible = editing
    self.cleaner_cost_text_box.visible = editing
    self.taxable_check_box.visible = editing
    self.save_row.visible = editing
    self.cancel_edit.visible = editing
    self.edit_row.visible = not editing
    self.deactivate_row.visible = not editing and self.item['active']
    self.activate_row.visible = not editing and not self.item['active']
    
    # Toggle visibility of display components
    self.name_label.visible = not editing
    self.matts_cost_label.visible = not editing
    self.cleaner_cost_label.visible = not editing
    self.taxable_label.visible = not editing
    
    if editing:
      # Show pennies divided by 100 in text boxes
      self.name_text_box.text = self.item['name']
      matts_pennies = self.item['mattsCost'] or 0
      cleaner_pennies = self.item['cleanerCost'] or 0
      self.matts_cost_text_box.text = f"{matts_pennies//100}.{matts_pennies%100:02d}"
      self.cleaner_cost_text_box.text = f"{cleaner_pennies//100}.{cleaner_pennies%100:02d}"
      self.taxable_check_box.checked = self.item['taxable']
      
  def enable_edit_mode(self):
    self.set_edit_mode(True)
    # Remove all event handler code - we're using buttons instead

  def cancel_edit_click(self, **event_args):
    """This method is called when the cancel button is clicked"""
    self.set_edit_mode(False)
    self.update_display()

  def edit_row_click(self, **event_args):
    self.enable_edit_mode()

  def save_row_click(self, **event_args):
    # Validate inputs
    if not all([self.name_text_box.text, self.matts_cost_text_box.text, self.cleaner_cost_text_box.text]):
      alert("All fields are required.")
      return
      
    try:
      # Convert dollar input to pennies using float * 100
      matts_cost = int(float(self.matts_cost_text_box.text) * 100)
      cleaner_cost = int(float(self.cleaner_cost_text_box.text) * 100)

      # Calculate minimum required matts_cost (130% of cleaner_cost)
      min_matts_cost = (cleaner_cost * 13 // 10)
      min_matts_dollars = f"${min_matts_cost//100}.{min_matts_cost%100:02d}"

      if matts_cost < min_matts_cost:
        alert(f"Pristine's cost must be at least {min_matts_dollars} based on the contractor cost entered.")
        return
        
      # Update on the server
      anvil.server.call(
        'update_billing_item',
        self.item.get_id(),
        self.name_text_box.text,
        matts_cost,
        cleaner_cost,
        self.taxable_check_box.checked
      )
      
      self.set_edit_mode(False)
      self.update_display()
      
    except ValueError:
      alert("Cost values must be valid numbers.")

  def deactivate_row_click(self, **event_args):
    anvil.server.call(
      'set_billing_item_active',
      self.item.get_id(),
      False
    )
    get_open_form().refresh_grid()

  def activate_row_click(self, **event_args):
    anvil.server.call(
      'set_billing_item_active',
      self.item.get_id(),
      True
    )
    get_open_form().refresh_grid()

  def form_show(self, **event_args):
    self.update_display()
