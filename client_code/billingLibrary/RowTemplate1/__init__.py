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
    
  def update_display(self):
    # Update labels
    self.name_label.text = self.item['name']
    self.matts_cost_label.text = f"${self.item['mattsCost']:.2f}"
    self.cleaner_cost_label.text = f"${self.item['cleanerCost']:.2f}"
    
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
    
    # Toggle visibility of display components
    self.name_label.visible = not editing
    self.matts_cost_label.visible = not editing
    self.cleaner_cost_label.visible = not editing
    
    if editing:
      # Populate text boxes
      self.name_text_box.text = self.item['name']
      self.matts_cost_text_box.text = str(self.item['mattsCost'])
      self.cleaner_cost_text_box.text = str(self.item['cleanerCost'])
      
  def enable_edit_mode(self):
    self.set_edit_mode(True)

  def edit_row_click(self, **event_args):
    self.enable_edit_mode()

  def save_row_click(self, **event_args):
    # Validate inputs
    if not all([self.name_text_box.text, self.matts_cost_text_box.text, self.cleaner_cost_text_box.text]):
      alert("All fields are required!")
      return
      
    try:
      matts_cost = float(self.matts_cost_text_box.text)
      cleaner_cost = float(self.cleaner_cost_text_box.text)
      
      if matts_cost < (cleaner_cost * 1.3):
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
    self.parent.parent.parent.refresh_grid()

  def activate_row_click(self, **event_args):
    anvil.server.call(
      'set_billing_item_active',
      self.item.get_id(),
      True
    )
    self.parent.parent.parent.refresh_grid()

  def form_show(self, **event_args):
    self.update_display()
