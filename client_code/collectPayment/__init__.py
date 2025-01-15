from ._anvil_designer import collectPaymentTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users


class collectPayment(collectPaymentTemplate):
  def create_invoice_button_click(self, **event_args):
    """
    Called when the 'Create Invoice' button is clicked.
    """
    line_items = [
        {"item_id": "1", "description": "Service A", "amount": 100.0, "quantity": 2},
        {"item_id": "2", "description": "Service B", "amount": 50.0, "quantity": 3}
    ]

    try:
        invoice = anvil.server.call('create_qbo_invoice', line_items)
        alert(f"Invoice created successfully! Invoice ID: {invoice['Id']}, Total: ${invoice['TotalAmt']:.2f}")
    except Exception as e:
        alert(f"Failed to create invoice: {e}")

