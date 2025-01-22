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
    # Initialize tax rate display
    self.load_tax_rate()
    # Set initial visibility
    self.tax_percentage_text_box.visible = False
    self.save_tax_rate.visible = False
    self.tax_percentage_label.visible = True
    self.edit_tax_rate.visible = True

  def load_tax_rate(self):
    """Load and display current tax rate"""
    current_rate = anvil.server.call('get_tax_rate')
    self.tax_percentage_label.text = f"{current_rate * 100:.3f}%"
    self.tax_percentage_text_box.text = f"{current_rate * 100:.3f}"

  def save_tax_rate_handler(self):
    """Handle saving the tax rate"""
    try:
      # Convert percentage input to decimal (e.g., 10.375% -> 0.10375)
      new_rate = float(self.tax_percentage_text_box.text.strip().replace('%', '')) / 100
      
      if new_rate < 0:
        alert("Tax rate cannot be negative.")
        return
      
      # Update the global tax rate and confirm the change
      updated_rate = anvil.server.call('update_tax_rate', new_rate)
      print(f"Tax rate updated to: {updated_rate}")  # Debug print
      
      # Update display and visibility
      self.load_tax_rate()
      self.tax_percentage_text_box.visible = False
      self.save_tax_rate.visible = False
      self.tax_percentage_label.visible = True
      self.edit_tax_rate.visible = True
      
    except ValueError:
      alert("Please enter a valid number.")
      return

  def edit_tax_rate_click(self, **event_args):
    """Show edit controls"""
    self.tax_percentage_text_box.visible = True
    self.save_tax_rate.visible = True
    self.tax_percentage_label.visible = False
    self.edit_tax_rate.visible = False
    self.tax_percentage_text_box.focus()

  def save_tax_rate_click(self, **event_args):
    self.save_tax_rate_handler()

  def tax_percentage_text_box_pressed_enter(self, **event_args):
    self.save_tax_rate_handler()
