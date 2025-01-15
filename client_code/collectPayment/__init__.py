from ._anvil_designer import collectPaymentTemplate
from anvil import *
import anvil.server
from datetime import datetime, timedelta

class collectPayment(collectPaymentTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.ACTIVE_CUSTOMER_MONTHS = 3
        self.SEARCH_MIN_CHARS = 3  # Minimum characters before searching
        
    def customer_selector_change(self, **event_args):
        """This method is called when the text in customer_selector changes"""
        search_text = self.customer_selector.text
        
        # Only search if we have enough characters
        if len(search_text) >= self.SEARCH_MIN_CHARS:
            try:
                matches = anvil.server.call('search_customers', search_text)
                if matches:
                    # Create dropdown panel with matches
                    dropdown_items = []
                    for match in matches:
                        dropdown_items.append({
                            'name': f"{match['firstName']} {match['lastName']}",
                            'email': match['email'],
                            'id': match['qbId']
                        })
                    # You'll need to implement the UI for showing these matches
                    # This could be a dropdown panel below the textbox
                    self.show_customer_matches(dropdown_items)
            except Exception as e:
                print(f"Error searching customers: {str(e)}")

    def show_customer_matches(self, matches):
        """Show matching customers in a dropdown panel"""
        # Implementation depends on your UI components
        # You might want to show/hide a repeating panel or dropdown below the textbox
        pass

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
