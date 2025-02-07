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
      
    # Set up input restrictions
    self.card_number_label.tag = {'prev_value': ''}
    self.expiration_label.tag = {'prev_value': ''}
    self.cvc_label.tag = {'prev_value': ''}
    self.zip_label.tag = {'prev_value': ''}

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

  def card_number_label_pressed_key(self, sender, key, **event_args):
    """Prevent non-numeric input in card number"""
    return key.lower() in '0123456789\b\r'

  def expiration_label_pressed_key(self, sender, key, **event_args):
    """Prevent non-numeric input in expiry date"""
    return key.lower() in '0123456789\b\r'

  def cvc_label_pressed_key(self, sender, key, **event_args):
    """Prevent non-numeric input in CVV"""
    return key.lower() in '0123456789\b\r'

  def zip_label_pressed_key(self, sender, key, **event_args):
    """Prevent non-numeric input in ZIP"""
    return key.lower() in '0123456789\b\r'

  def show_card_number_click(self, **event_args):
    """Show full card number"""
    self.card_number_hidden = False
    if hasattr(self, 'show_card_number'):
        self.show_card_number.visible = False
    if hasattr(self, 'hide_card_number'):
        self.hide_card_number.visible = True
    self.card_number_label_lost_focus()

  def hide_card_number_click(self, **event_args):
    """Hide card number"""
    self.card_number_hidden = True
    if hasattr(self, 'show_card_number'):
        self.show_card_number.visible = True
    if hasattr(self, 'hide_card_number'):
        self.hide_card_number.visible = False
    self.card_number_label_lost_focus()

  def validate_card_number(self):
    """Validate card number and return True if valid"""
    if not self.is_valid_card_number(self.card_number_label.text):
      self.card_number_label.background = '#fff0f0'  # Light red
      alert("Please enter a valid card number")
      return False
    return True

  def validate_expiration(self):
    """Validate expiration date and return True if valid"""
    cleaned = re.sub(r'\D', '', self.expiration_label.text)
    if not cleaned.isdigit() or len(cleaned) != 4:
      self.expiration_label.background = '#fff0f0'
      alert("Please enter a valid expiration date (MM/YY)")
      return False
    
    month, year = int(cleaned[:2]), int(cleaned[2:])
    exp_date = datetime(2000 + year, month, 1)
    if exp_date <= datetime.now():
      self.expiration_label.background = '#fff0f0'
      alert("Card has expired")
      return False
    return True

  def validate_cvc(self):
    """Validate CVC and return True if valid"""
    cleaned = self.cvc_label.text
    if not cleaned.isdigit():
        self.cvc_label.background = '#fff0f0'
        alert("Please enter only numbers for CVC")
        return False
    required_length = 4 if hasattr(self, 'card_type') and self.card_type == 'Amex' else 3
    if len(cleaned) != required_length:
      self.cvc_label.background = '#fff0f0'
      alert(f"Please enter a valid {required_length}-digit security code")
      return False
    return True

  def validate_zip(self):
    """Validate ZIP code and return True if valid"""
    if not self.zip_label.text.isdigit() or len(self.zip_label.text) != 5:
      self.zip_label.background = '#fff0f0'
      alert("Please enter a valid 5-digit ZIP code")
      return False
    return True

  def validate_name(self):
    """Validate card holder name and return True if valid"""
    cleaned = self.name_on_card_label.text.strip()
    if len(cleaned) < 2 or not any(c.isalpha() for c in cleaned):
      self.name_on_card_label.background = '#fff0f0'
      alert("Please enter a valid name")
      return False
    return True

  # Add lost_focus event handlers
  def card_number_label_lost_focus(self, **event_args):
    """Validate card number when focus is lost"""
    self.validate_card_number()

  def expiration_label_lost_focus(self, **event_args):
    """Validate expiration when focus is lost"""
    self.validate_expiration()

  def cvc_label_lost_focus(self, **event_args):
    """Validate CVC when focus is lost"""
    self.validate_cvc()

  def zip_label_lost_focus(self, **event_args):
    """Validate ZIP when focus is lost"""
    self.validate_zip()

  def name_on_card_label_lost_focus(self, **event_args):
    """Validate name when focus is lost"""
    self.validate_name()

  def process_payment_click(self, **event_args):
    """Validate all fields before processing"""
    # Validate all fields in sequence
    if not (self.validate_card_number() and 
            self.validate_expiration() and 
            self.validate_cvc() and 
            self.validate_zip() and 
            self.validate_name()):
      return
      
    # Continue with payment processing
    # ...existing payment processing code...

  def cancel_button_click(self, **event_args):
    """Handle cancel button click"""
    if confirm("Are you sure you want to cancel? The invoice has already been created."):
      open_form('landingPage')
