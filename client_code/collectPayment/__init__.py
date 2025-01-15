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

  def create_customer_button_click(self, **event_args):
    """
    This method is called when the 'Create Customer' button is clicked.
    """
    first_name = self.first_name_input.text
    last_name = self.last_name_input.text
    email = self.email_input.text

    # Validate inputs
    if not first_name or not last_name or not email:
        alert("Please fill in all fields: First Name, Last Name, and Email.")
        return

    try:
        # Call the server function to create a customer
        customer_data = anvil.server.call('create_qbo_customer', first_name, last_name, email)

        # Add the customer to the Anvil Data Table
        app_tables.customers.add_row(
            stripeId=customer_data["Id"],  # The QBO Customer ID
            firstName=first_name,
            lastName=last_name,
            email=email
        )

        alert(f"Customer created successfully! Customer ID: {customer_data['Id']}")

    except Exception as e:
        alert(f"Failed to create customer: {e}")
