from ._anvil_designer import cardInfoTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class cardInfo(cardInfoTemplate):
  def __init__(self, invoice_id=None, amount=0, customer=None, **properties):
    self.init_components(**properties)
    self.invoice_id = invoice_id
    self.amount = amount
    self.customer = customer
    
    # Set up form with passed data
    if customer:
      self.customer_name_label.text = f"{customer['firstName']} {customer['lastName']}"
    if amount:
      self.amount_label.text = f"${amount//100}.{amount%100:02d}"

  def process_payment_click(self, **event_args):
    """Handle payment processing"""
    try:
      # Validate card info (add your validation logic here)
      if not all([self.card_number_input.text,
                  self.expiry_date_input.text,
                  self.cvv_input.text,
                  self.name_on_card_input.text]):
        alert("Please fill in all card details")
        return
        
      # TODO: Add actual payment processing logic here
      
      alert("Payment processed successfully!")
      # Return to previous form or close
      open_form('landingPage')
      
    except Exception as e:
      alert(f"Payment processing failed: {str(e)}")

  def cancel_button_click(self, **event_args):
    """Handle cancel button click"""
    if confirm("Are you sure you want to cancel? The invoice has already been created."):
      open_form('landingPage')
