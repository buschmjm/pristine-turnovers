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
    self.edit_row.visible = True
    self.save_row.visible = False
    
  def update_display(self):
    name = self.item['name']
    matts_pennies = self.item['mattsCost'] or 0
    cleaner_pennies = self.item['cleanerCost'] or 0

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
    self.save_row.visible = editing
    self.edit_row.visible = not editing
    
    # Toggle visibility of display components
    self.name_label.visible = not editing
    self.matts_cost_label.visible = not editing
    self.cleaner_cost_label.visible = not editing
    
    if editing:
      # Show pennies divided by 100 in text boxes
      self.name_text_box.text = self.item['name']
      matts_pennies = self.item['mattsCost'] or 0
      cleaner_pennies = self.item['cleanerCost'] or 0
      self.matts_cost_text_box.text = f"{matts_pennies//100}.{matts_pennies%100:02d}"
      self.cleaner_cost_text_box.text = f"{cleaner_pennies//100}.{cleaner_pennies%100:02d}"
      
  def enable_edit_mode(self):
    self.set_edit_mode(True)
    # Add focus handler to detect clicks outside
    self.parent.parent.set_event_handler('lost_focus', self.cancel_edit)

  def cancel_edit(self, **event_args):
    """Cancel editing when clicking outside"""
    self.set_edit_mode(False)
    self.update_display()

  def edit_row_click(self, **event_args):
    self.enable_edit_mode()

  def save_row_click(self, **event_args):
    # Validate inputs
    if not all([self.name_text_box.text, self.matts_cost_text_box.text, self.cleaner_cost_text_box.text]):
      alert("All fields are required!")
      return
      
    try:
      # Convert dollar input to pennies using float * 100
      matts_cost = int(float(self.matts_cost_text_box.text) * 100)
      cleaner_cost = int(float(self.cleaner_cost_text_box.text) * 100)

      # Check 30% markup using integer math
      if matts_cost < (cleaner_cost * 13 // 10):
        alert("Matt's cost must be at least 30% higher than cleaner cost!")
        return
        
      # Update on the server
      anvil.server.call(
        'update_billing_item',
        self.item.get_id(),
        self.name_text_box.text,
        matts_cost,
        cleaner_cost
      )
      
      self.set_edit_mode(False)
      self.update_display()
      
    except ValueError:
      alert("Cost values must be valid numbers!")

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
