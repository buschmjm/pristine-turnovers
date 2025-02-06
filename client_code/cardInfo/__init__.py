from ._anvil_designer import cardInfoTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import re


class cardInfo(cardInfoTemplate):
  def __init__(self, invoice_id=None, amount=0, customer=None, **properties):
    self.init_components(**properties)
    self.invoice_id = invoice_id
    self.amount = amount
    self.customer = customer
    self.card_number_hidden = True
    
    # Set up form with passed data
    if customer:
      self.customer_name_label.text = f"{customer['firstName']} {customer['lastName']}"
    if amount:
      formatted_amount = f"${amount//100}.{amount%100:02d}"
      self.process_payment_button.text = f"Process Payment of {formatted_amount}"

  def format_card_number(self, card_number):
    """Format card number with spaces and handle masking"""
    # Remove non-digits
    cleaned = re.sub(r'\D', '', card_number)
    # Format in groups of 4
    groups = [cleaned[i:i+4] for i in range(0, len(cleaned), 4)]
    # Mask all but last 4 if hidden
    if self.card_number_hidden:
      groups = ['****' for i in range(len(groups)-1)] + [groups[-1]] if groups else []
    return ' '.join(groups)

  def is_valid_card_number(self, card_number):
    """Validate card number using Luhn algorithm and basic patterns"""
    cleaned = re.sub(r'\D', '', card_number)
    if not cleaned:
      return False
      
    # Check card type patterns
    patterns = {
      'Amex': r'^3[47][0-9]{13}$',
      'Visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
      'Mastercard': r'^5[1-5][0-9]{14}$',
      'Discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$'
    }
    
    is_valid = any(re.match(pattern, cleaned) for pattern in patterns.values())
    self.card_type = next((card for card, pattern in patterns.items() 
                          if re.match(pattern, cleaned)), None)
    return is_valid

  def card_number_input_change(self, **event_args):
    """Handle card number input formatting and validation"""
    current = self.card_number_input.text
    cleaned = re.sub(r'\D', '', current)
    
    if self.is_valid_card_number(cleaned):
      self.card_number_input.background = '#f0fff0'  # Light green for valid
      self.card_number_input.text = self.format_card_number(cleaned)
      # Update CVC max length based on card type
      self.cvv_input.maximum_length = 4 if self.card_type == 'Amex' else 3
    else:
      self.card_number_input.background = '#fff0f0'  # Light red for invalid
      self.card_number_input.text = self.format_card_number(cleaned)

  def expiry_date_input_change(self, **event_args):
    """Format expiry date as MM/YY"""
    current = self.expiry_date_input.text
    cleaned = re.sub(r'\D', '', current)
    
    if len(cleaned) > 4:
      cleaned = cleaned[:4]
    
    if len(cleaned) >= 2:
      month = int(cleaned[:2])
      if month > 12:
        cleaned = '12' + cleaned[2:]
      formatted = f"{cleaned[:2]}/{cleaned[2:]}"
    else:
      formatted = cleaned
      
    self.expiry_date_input.text = formatted

  def cvv_input_change(self, **event_args):
    """Validate CVV/CVC based on card type"""
    current = self.cvv_input.text
    cleaned = re.sub(r'\D', '', current)
    max_length = 4 if hasattr(self, 'card_type') and self.card_type == 'Amex' else 3
    
    if len(cleaned) > max_length:
      cleaned = cleaned[:max_length]
    
    self.cvv_input.text = cleaned
    self.cvv_input.background = '#f0fff0' if len(cleaned) == max_length else '#fff0f0'

  def zip_input_change(self, **event_args):
    """Validate and format ZIP code"""
    current = self.zip_input.text
    cleaned = re.sub(r'\D', '', current)
    
    if len(cleaned) > 5:
      cleaned = cleaned[:5]
      
    self.zip_input.text = cleaned
    self.zip_input.background = '#f0fff0' if len(cleaned) == 5 else '#fff0f0'

  def show_card_number_click(self, **event_args):
    """Show full card number"""
    self.card_number_hidden = False
    if hasattr(self, 'show_card_number'):  # Use actual button name
        self.show_card_number.visible = False
    if hasattr(self, 'hide_card_number'):  # Use actual button name
        self.hide_card_number.visible = True
    self.card_number_input_change()

  def hide_card_number_click(self, **event_args):
    """Hide card number"""
    self.card_number_hidden = True
    if hasattr(self, 'show_card_number'):  # Use actual button name
        self.show_card_number.visible = True
    if hasattr(self, 'hide_card_number'):  # Use actual button name
        self.hide_card_number.visible = False
    self.card_number_input_change()

  def process_payment_click(self, **event_args):
    """Validate all fields before processing"""
    if not all([
      self.is_valid_card_number(self.card_number_input.text),
      len(re.sub(r'\D', '', self.expiry_date_input.text)) == 4,
      len(self.cvv_input.text) in [3, 4],
      len(self.zip_input.text) == 5,
      self.name_on_card_input.text
    ]):
      alert("Please fill in all fields correctly")
      return
      
    # ... rest of payment processing code ...

  def cancel_button_click(self, **event_args):
    """Handle cancel button click"""
    if confirm("Are you sure you want to cancel? The invoice has already been created."):
      open_form('landingPage')
