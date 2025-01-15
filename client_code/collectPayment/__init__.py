from ._anvil_designer import collectPaymentTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

class collectPayment(collectPaymentTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    try:
        # Fetch billing items from the server
        billing_items = anvil.server.call('get_billing_items')

        # Display billing items for selection
        selected_items = self.show_billing_item_selector(billing_items)

        if not selected_items:
            alert("No items selected for billing.")
            return

        # Calculate total amount based on selected items
        total_amount = sum(item['amount'] for item in selected_items)

        # Process payment
        charge = stripe.checkout.charge(
            currency="USD",
            amount=total_amount,
            title="Acme Store",
            description=", ".join(item['description'] for item in selected_items),
            zipcode=True,
            billing_address=True
        )

        print(charge["url"])

    except anvil.server.AnvilWrappedError as e:
        alert(f"Failed to retrieve or process billing items: {e}")

def show_billing_item_selector(self, billing_items):
    """
    Displays a dialog for selecting billing items.

    Args:
        billing_items (list): List of billing items fetched from Stripe.

    Returns:
        list: List of selected items.
    """
    # Example of simple item selection logic; replace with your UI logic
    selected_items = []
    for item in billing_items:
        if confirm(f"Add {item['description']} (${item['amount']/100:.2f}) to the payment?"):
            selected_items.append(item)
    return selected_items
