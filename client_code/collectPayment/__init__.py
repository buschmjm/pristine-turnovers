from ._anvil_designer import collectPaymentTemplate
from anvil import *
import anvil.server
from datetime import datetime, timedelta

class collectPayment(collectPaymentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        # Configuration variable for active customer timeframe (in months)
        self.ACTIVE_CUSTOMER_MONTHS = 3
        
        # Populate customer selector
        self.populate_customer_selector()

    def populate_customer_selector(self):
        """Populate the customer dropdown with recent customers."""
        try:
            recent_customers = anvil.server.call('get_recent_customers', self.ACTIVE_CUSTOMER_MONTHS)
            
            # Add a blank option at the start
            self.customer_selector.items = [{'value': '', 'text': '-- Select Customer --'}] + recent_customers
            
        except Exception as e:
            alert(f"Failed to load customer list: {str(e)}")

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

        if not first_name or not last_name or not email:
            alert("Please fill in all fields: First Name, Last Name, and Email.")
            return

        try:
            result = anvil.server.call('create_and_store_customer', first_name, last_name, email)
            if result["success"]:
                alert(f"Customer created successfully!\nCustomer ID: {result['customerId']}")
                # Optional: Clear the form after successful creation
                self.first_name_input.text = ""
                self.last_name_input.text = ""
                self.email_input.text = ""
        except Exception as e:
            error_message = str(e)
            if "already exists in QuickBooks Online" in error_message:
                alert(error_message)
            elif "email already exists" in error_message.lower():
                alert("This email address is already associated with a customer in QuickBooks Online. "
                     "Please use a different email or contact support if you believe this is an error.")
            else:
                alert(f"Failed to create customer: {error_message}")
