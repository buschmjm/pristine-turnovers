from ._anvil_designer import RowTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate2(RowTemplate2Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    if not self.item or 'billing_item' not in self.item:
      self.setup_initial_state()
    else:
      self.update_display()

  def setup_initial_state(self):
    """Set up initial component visibility for new rows"""
    # Show edit panel, hide display panel
    self.edit_item_panel.visible = True
    self.display_item_panel.visible = False
    
    # Load dropdown options
    billing_items = anvil.server.call('get_active_billing_items_for_dropdown')
    print(f"Loaded {len(items)} items for dropdown")
    self.add_item_selector_dropdown.items = [
      (item['display'], item['value']) for item in billing_items
    ]
    self.quantity_entry_box.text = "1"

  def calculate_total(self):
    """Calculate total cost including tax"""
    quantity = int(self.quantity_entry_box.text or 1)
    selected_item = self.item['billing_item']
    cost_each = selected_item['mattsCost']
    tax = selected_item['taxable'] * 0  # Placeholder for tax calculation
    return (cost_each * quantity) + tax
    
  def update_display(self):
    """Update all display fields"""
    if not self.item or 'billing_item' not in self.item:
      return
      
    selected_item = self.item['billing_item']
    if not selected_item:
      return
      
    quantity = int(self.quantity_entry_box.text or 1)
    
    self.billing_item_name_label.text = selected_item['name']
    self.cost_each_label.text = f"${selected_item['mattsCost']//100}.{selected_item['mattsCost']%100:02d}"
    self.tax_cost_label.text = f"${0:.2f}" if not selected_item['taxable'] else f"${0:.2f}"
    total = self.calculate_total()
    self.item_total_label.text = f"${total//100}.{total%100:02d}"
    
  def add_item_selector_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def edit_billing_item_click(self, **event_args):
    """Re-open edit panel when edit button is clicked"""
    self.edit_item_panel.visible = True
    self.display_item_panel.visible = False
    
    # Load current values into edit fields
    self.add_item_selector_dropdown.selected_value = (
      f"{self.item['billing_item']['name']} - ${self.item['billing_item']['mattsCost']//100}.{self.item['billing_item']['mattsCost']%100:02d}",
      self.item['billing_item']
    )
    self.quantity_entry_box.text = str(self.item.get('quantity', 1))

  def quantity_entry_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  def quantity_entry_box_change(self, **event_args):
    """Validate and update quantity"""
    try:
      quantity = int(self.quantity_entry_box.text or 1)
      if quantity < 1:
        self.quantity_entry_box.text = "1"
      self.update_display()
    except ValueError:
      self.quantity_entry_box.text = "1"
      self.update_display()

  def save_billing_item_click(self, **event_args):
    """Save the selected item details"""
    if not self.add_item_selector_dropdown.selected_value:
      alert("Please select an item.")
      return
    
    print(f"Selected item: {self.add_item_selector_dropdown.selected_value}")  # Debug print
    
    # The selected value now contains the full item data
    selected_item = self.add_item_selector_dropdown.selected_value
    
    # Update the item dictionary
    if isinstance(self.item, dict):
      self.item['billing_item'] = selected_item
    else:
      self.item = {'billing_item': selected_item}
    
    # Switch panel visibility
    self.edit_item_panel.visible = False
    self.display_item_panel.visible = True
    
    self.update_display()

  def delete_billing_item_click(self, **event_args):
    """Remove this row"""
    get_open_form().remove_bill_item(self.item)
