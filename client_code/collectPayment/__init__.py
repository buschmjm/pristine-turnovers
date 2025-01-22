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
        self.customer_table.visible = True
        self.bill_items = []  # Initialize empty list for bill items
        print("Initializing bill_items_list...")  # Debug print
        if hasattr(self, 'bill_items_list'):
            self.bill_items_list.items = self.bill_items
            self.bill_items_list.role = 'multiple'  # Ensure proper list mode
            print("bill_items_list initialized")  # Debug print
        else:
            print("Error: bill_items_list component not found!")  # Debug print
            
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
            
    def refresh_customer_list(self):
        """Refresh just the customer list component"""
        # Use background task to load customers
        customers = anvil.server.call('customerQueries')
        self.repeating_panel_1.items = customers if customers else []
            
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
                
                # Refresh the customer list in the background
                self.refresh_customer_list()
                
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
        
    def clear_customer_highlights(self):
        """Clear highlighting from all customer rows"""
        for c in self.repeating_panel_1.get_components():
            c.background = 'white'
            
    def select_customer(self, customer, row_template=None):
        """Handle customer selection from template"""
        self.selected_customer = customer
        
        # Clear all previous highlighting first
        self.clear_customer_highlights()
        
        # Set new highlight if row provided
        if row_template:
            row_template.background = '#E3F2FD'
            self.selected_row = row_template
        
        # Hide customer selection card and show billing
        self.customer_card.visible = False
        self.selected_customer_label.text = f"Bill for {customer['firstName']} {customer['lastName']}"
        self.bill_card.visible = True
        self.re_select_customer_button.visible = True
        
        # Clear any existing bill items when selecting new customer
        self.bill_items = []
        self.bill_items_list.items = self.bill_items
        
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

    def refresh_bill_items(self):
        """Refresh the bill items grid"""
        temp_items = list(self.bill_items)  # Create a new list instance
        self.bill_items_list.items = None   # Clear the list
        self.bill_items_list.items = temp_items  # Set new list
    
    def add_bill_item_button_click(self, **event_args):
        """Add a new blank row to the bill items table"""
        print("Adding new bill item...")  # Debug print
        new_item = {'billing_item': None}
        self.bill_items.append(new_item)
        print(f"Current bill items count: {len(self.bill_items)}")  # Debug print
        self.refresh_bill_items()
        print("Refreshed bill_items_list")

    def remove_bill_item(self, item):
        """Remove an item from the bill items list"""
        if item in self.bill_items:
            self.bill_items.remove(item)
            self.refresh_bill_items()

    def proceed_payment_card_button_click(self, **event_args):
      """This method is called when the button is clicked"""
      pass
