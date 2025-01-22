from ._anvil_designer import collectPaymentTemplate
from anvil import *
import anvil.server
from datetime import datetime, timedelta
from anvil.tables import app_tables

class collectPayment(collectPaymentTemplate):
    def __init__(self, **properties):
        print("Starting form initialization...")  # Debug print
        self.init_components(**properties)
        self.show_existing_customer()
        
        # Simple direct load without delayed loading
        self.load_customers()
        print("Form initialization complete")  # Debug print
        self.selected_customer = None
        self.bill_card.visible = False  # Ensure bill card starts hidden
        self.selected_row = None  # Track selected row for highlighting
            
    def load_customers(self):
        """Load all customers into the repeating panel"""
        print("Starting customer load...")  # Debug print
        try:
            customers = anvil.server.call("customerQueries")
            print(f"Retrieved {len(customers)} customers")  # Debug print
            self.repeating_panel_1.items = customers if customers else []
        except Exception as e:
            print(f"Error loading customers: {str(e)}")  # Debug print
            alert("Failed to load customers. Please try refreshing the page.")
            
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
                # Create a customer object that matches our expected format
                new_customer = {
                    'firstName': first_name,
                    'lastName': last_name,
                    'email': email,
                    'id': result['customerId']
                }
                
                # Select the new customer and move to billing
                self.select_customer(new_customer)
                
                # Clear the form
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

    def show_existing_customer(self):
        """Show existing customer card and hide new customer card"""
        self.existing_customer.visible = True
        self.new_customer.visible = False
        # Update button states
        self.existing_customer_button.background = '#2196F3'  # Active blue color
        self.existing_customer_button.foreground = 'white'
        self.new_customer_button.background = 'white'
        self.new_customer_button.foreground = 'black'
        
    def show_new_customer(self):
        """Show new customer card and hide existing customer card"""
        self.existing_customer.visible = False
        self.new_customer.visible = True
        # Update button states
        self.new_customer_button.background = '#2196F3'  # Active blue color
        self.new_customer_button.foreground = 'white'
        self.existing_customer_button.background = 'white'
        self.existing_customer_button.foreground = 'black'
        
    def existing_customer_button_click(self, **event_args):
        """Called when the existing customer button is clicked"""
        self.show_existing_customer()
        
    def new_customer_button_click(self, **event_args):
        """Called when the new customer button is clicked"""
        self.show_new_customer()
        
    def select_customer(self, customer, row_template=None):
        """Handle customer selection from template"""
        self.selected_customer = customer
        
        # Update highlighting - remove previous and set new
        if self.selected_row:
            self.selected_row.background = 'white'
        if row_template:
            row_template.background = '#E3F2FD'  # Light blue highlight
            self.selected_row = row_template
        
        # Hide customer selection card and show billing
        self.customer_card.visible = False
        self.selected_customer_label.text = f"Bill for {customer['firstName']} {customer['lastName']}"
        self.bill_card.visible = True
        self.re_select_customer_button.visible = True
        
    def re_select_customer_button_click(self, **event_args):
        """Handle customer reselection"""
        # Reset UI state including row highlighting
        if self.selected_row:
            self.selected_row.background = 'white'
            self.selected_row = None
        # Reset UI state
        self.customer_card.visible = True
        self.bill_card.visible = False
        self.re_select_customer_button.visible = False
        self.selected_customer_label.text = ""
        self.selected_customer = None
        self.show_existing_customer()  # Return to existing customer view
