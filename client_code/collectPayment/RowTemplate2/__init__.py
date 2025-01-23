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
    # Show edit panel with dropdown and quantity box
    self.edit_item_panel.visible = True
    
    # Hide display components
    self.billing_item_name_label.visible = False
    self.cost_each_label.visible = False
    self.quantity_label.visible = False  # Hide quantity label
    self.tax_cost_label.visible = False
    self.item_total_label.visible = False
    self.edit_billing_item.visible = False
    
    # Load dropdown options
    billing_items = anvil.server.call('get_active_billing_items_for_dropdown')
    formatted_items = []
    for item in billing_items:
      # Create display string
      display = item['display']
      # Create tuple of (display string, value dictionary)
      formatted_items.append((display, item['value']))
    
    self.add_item_selector_dropdown.items = formatted_items
    
    # Set default quantity
    self.quantity_entry_box.text = "1"
    if isinstance(self.item, dict):
      self.item['quantity'] = 1

  def calculate_total(self):
    """Calculate total cost including tax"""
    quantity = int(self.quantity_entry_box.text or 1)
    selected_item = self.item['billing_item']
    cost_each = selected_item['mattsCost']
    subtotal = cost_each * quantity
    
    # Get tax rate and calculate tax if item is taxable
    if selected_item['taxable']:
      tax_rate = anvil.server.call('get_tax_rate')
      tax = int(subtotal * tax_rate)  # Convert to pennies
    else:
      tax = 0
      
    return subtotal + tax
    
  def update_display(self):
    """Update all display fields"""
    if not self.item or 'billing_item' not in self.item:
      return
      
    selected_item = self.item['billing_item']
    if not selected_item:
      return
    
    # Display item details
    self.billing_item_name_label.text = selected_item['name']
    self.cost_each_label.text = f"${selected_item['mattsCost']//100}.{selected_item['mattsCost']%100:02d}"
    self.quantity_label.text = str(self.item.get('quantity', 1))
    
    # Display tax and total
    subtotal = selected_item['mattsCost'] * self.item.get('quantity', 1)
    tax_amount = self.item.get('tax_amount', 0)
    self.tax_cost_label.text = f"${tax_amount//100}.{tax_amount%100:02d}"
    total = subtotal + tax_amount
    self.item_total_label.text = f"${total//100}.{total%100:02d}"
    
  def add_item_selector_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  def edit_billing_item_click(self, **event_args):
    """Re-open edit panel when edit button is clicked"""
    # Show edit panel, hide display components
    self.edit_item_panel.visible = True
    self.billing_item_name_label.visible = False
    self.cost_each_label.visible = False
    self.quantity_label.visible = False
    self.tax_cost_label.visible = False
    self.item_total_label.visible = False
    self.edit_billing_item.visible = False
    
    # Load current values
    current_item = self.item['billing_item']
    
    # Rebuild the dropdown option in same format as initial loading
    display_text = f"{current_item['name']} - ${current_item['mattsCost']//100}.{current_item['mattsCost']%100:02d}"
    
    # Reload dropdown options to ensure we have fresh data
    billing_items = anvil.server.call('get_active_billing_items_for_dropdown')
    formatted_items = []
    for item in billing_items:
      formatted_items.append((item['display'], item['value']))
    
    self.add_item_selector_dropdown.items = formatted_items
    
    # Find and select the matching item
    for display, value in formatted_items:
      if value['name'] == current_item['name']:
        self.add_item_selector_dropdown.selected_value = value
        break
        
    self.quantity_entry_box.text = str(self.item.get('quantity', 1))
    get_open_form().proceed_payment_card_button.visible = False

  def quantity_entry_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  def quantity_entry_box_change(self, **event_args):
    """Validate and update quantity"""
    try:
      quantity = int(self.quantity_entry_box.text or 1)
      if quantity < 1:
        self.quantity_entry_box.text = "1"
      self.item['quantity'] = quantity  # Store quantity in item data
      self.update_display()  # Refresh tax and total
    except ValueError:
      self.quantity_entry_box.text = "1"
      self.item['quantity'] = 1
      self.update_display()

  def save_billing_item_click(self, **event_args):
    if not self.add_item_selector_dropdown.selected_value:
      alert("Please select an item.")
      return
    
    # Get the selected item data
    selected_item = self.add_item_selector_dropdown.selected_value
    quantity = int(self.quantity_entry_box.text or 1)
    
    # Calculate tax
    subtotal = selected_item['mattsCost'] * quantity
    if selected_item['taxable']:
      tax_rate = anvil.server.call('get_tax_rate')
      tax_amount = int(subtotal * tax_rate)
    else:
      tax_amount = 0
    
    # Update item data
    self.item.update({
      'billing_item': selected_item,
      'quantity': quantity,
      'tax_amount': tax_amount
    })
    
    # Switch visibility
    self.edit_item_panel.visible = False
    self.billing_item_name_label.visible = True
    self.cost_each_label.visible = True
    self.quantity_label.visible = True
    self.tax_cost_label.visible = True
    self.item_total_label.visible = True
    self.edit_billing_item.visible = True
    
    self.update_display()
    get_open_form().show_add_button()

  def delete_billing_item_click(self, **event_args):
    """Remove this row"""
    get_open_form().remove_bill_item(self.item)
    # Show add and proceed buttons after delete
    get_open_form().show_add_button()
  def delete_billing_item_click(self, **event_args):

    """Remove this row"""
    get_open_form().remove_bill_item(self.item)
    # Show add and proceed buttons after delete
    get_open_form().show_add_button()
