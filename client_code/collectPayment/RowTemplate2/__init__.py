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
    # Load dropdown options first to ensure we have data
    items = anvil.server.call('get_active_billing_items_for_dropdown')
    print(f"Loaded {len(items)} items for dropdown")  # Debug print
    
    # Show only necessary components for new row
    self.add_item_selector_dropdown.visible = True
    self.save_billing_item.visible = True
    self.delete_billing_item.visible = True
    
    # Hide all other components
    self.billing_item_name_label.visible = False
    self.edit_billing_item.visible = False  # Always hide edit button for new items
    self.cost_each_label.visible = False
    self.quantity_entry_box.visible = False
    self.tax_cost_label.visible = False
    self.item_total_label.visible = False
    
    # Set dropdown items directly from server response
    dropdown_items = []
    for item in items:
      display_text = item['display']
      value = item['value']
      print(f"Adding item to dropdown: {display_text}")  # Debug print
      dropdown_items.append((display_text, value))
    
    self.add_item_selector_dropdown.items = dropdown_items
    
    # Set default quantity
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
    """This method is called when the button is clicked"""
    pass

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
    
    # Switch visibility and update display
    self.add_item_selector_dropdown.visible = False
    self.billing_item_name_label.visible = True
    self.edit_billing_item.visible = True
    self.cost_each_label.visible = True
    self.quantity_entry_box.visible = True
    self.tax_cost_label.visible = True
    self.item_total_label.visible = True
    self.save_billing_item.visible = False
    
    self.update_display()

  def delete_billing_item_click(self, **event_args):
    """Remove this row"""
    get_open_form().remove_bill_item(self.item)
