from ._anvil_designer import collectPaymentTemplate
from anvil import *
import anvil.server
from datetime import datetime, timedelta
from anvil.tables import app_tables

class collectPayment(collectPaymentTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.show_existing_customer()
        self.load_customers()
        self.selected_customer = None
        self.bill_items = []
        self.setup_initial_state()
    
    def setup_initial_state(self):
        """Initialize form state"""
        self.bill_card.visible = False
        self.customer_table.visible = True
        self.repeating_panel_2.items = self.bill_items
        self.update_totals()  # Initialize totals
            
    def load_customers(self):
        """Load all customers into the repeating panel"""
        print("Starting customer load...")
        try:
            # Get customers from server
            customers = anvil.server.call("customerQueries")
            print(f"Retrieved {len(customers)} customers")
            
            if customers:
                # Sort customers by last name
                sorted_customers = sorted(customers, key=lambda x: x['lastName'])
                print("Customers sorted successfully")
                
                # Update repeating panel
                self.repeating_panel_1.items = sorted_customers
                print("Repeating panel updated")
            else:
                print("No customers returned from server")
                self.repeating_panel_1.items = []
                
        except Exception as e:
            print(f"Error loading customers: {str(e)}")
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
        """Handle customer creation"""
        first_name = self.first_name_input.text
        last_name = self.last_name_input.text
        email = self.email_input.text
        
        if not all([first_name, last_name, email]):
            alert("Please fill in all fields")
            return
            
        try:
            result = anvil.server.call('create_and_store_customer', first_name, last_name, email)
            if result["success"]:
                # Select the new customer and move to billing
                self.select_customer(result["customerData"])
                # Clear form
                self.first_name_input.text = ""
                self.last_name_input.text = ""
                self.email_input.text = ""
                # Refresh list
                self.refresh_customer_list()
                
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower():
                # Try to find and sync existing customer
                try:
                    customer = anvil.server.call('find_qbo_customer_by_email', email)
                    if customer:
                        alert("Customer found in QuickBooks. Syncing records...")
                        self.select_customer(customer)
                    else:
                        alert("Error: Customer exists but could not be found")
                except Exception as sync_error:
                    alert(f"Error syncing customer: {str(sync_error)}")
            else:
                alert(f"Failed to create customer: {error_msg}")

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
        # Try to ensure customer has QBO ID
        try:
            if not hasattr(customer, 'qbId'):
                has_qbo = anvil.server.call('ensure_customer_qbo_id', customer)
                if not has_qbo:
                    alert("Customer not found in QuickBooks. Please create the customer first.")
                    self.show_new_customer()
                    # Pre-fill the form
                    self.first_name_input.text = customer['firstName']
                    self.last_name_input.text = customer['lastName']
                    self.email_input.text = customer['email']
                    return
                    
            # Convert LiveObjectProxy to dict for easier handling
            self.selected_customer = {
                'firstName': customer['firstName'],
                'lastName': customer['lastName'],
                'email': customer['email'],
                'qbId': customer['qbId']
            }
            
            # Rest of the selection process
            # ...existing code...
            
        except Exception as e:
            alert(f"Error selecting customer: {str(e)}")
        
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
        self.update_totals()  # Reset totals for new customer
        
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
        """Refresh the bill items panel"""
        temp_items = list(self.bill_items)
        self.repeating_panel_2.items = temp_items
    
    def add_bill_item_button_click(self, **event_args):
        """Add a new blank row to the bill items list"""
        print("Adding new bill item...")
        
        # Save current quantities before refresh
        current_quantities = {
            item['billing_item']['name']: item.get('quantity', 1) 
            for item in self.bill_items if 'billing_item' in item
        }
        
        # Add new item
        new_item = {'billing_item': None}
        self.bill_items.append(new_item)
        
        # Hide buttons
        self.add_bill_item_button.visible = False
        self.proceed_payment_card_button.visible = False
        
        # Update panel and restore quantities
        self.repeating_panel_2.items = None
        self.repeating_panel_2.items = self.bill_items
        
        # Restore quantities and setup new row
        for component in self.repeating_panel_2.get_components():
            if component.item == new_item:
                component.setup_initial_state()
            elif 'billing_item' in component.item:
                item_name = component.item['billing_item']['name']
                if item_name in current_quantities:
                    component.quantity_entry_box.text = str(current_quantities[item_name])
                    component.item['quantity'] = current_quantities[item_name]
                    component.update_display()
        
        print("Bill items refreshed")
        self.update_totals()  # Update totals after adding item

    def show_add_button(self):
        """Helper to show add and proceed buttons after save/delete"""
        self.add_bill_item_button.visible = True
        self.proceed_payment_card_button.visible = True

    def remove_bill_item(self, item):
        """Remove an item from the bill items list"""
        if item in self.bill_items:
            self.bill_items.remove(item)
            self.repeating_panel_2.items = self.bill_items
            self.update_totals()  # Update totals after removing item

    def calculate_bill_totals(self):
        """Calculate subtotal, tax total and grand total for all items"""
        subtotal = 0
        tax_total = 0
        
        for item in self.bill_items:
            if 'billing_item' not in item:
                continue
            quantity = item.get('quantity', 1)
            cost = item['billing_item']['mattsCost']
            subtotal += cost * quantity
            tax_total += item.get('tax_amount', 0)
            
        return {
            'subtotal': subtotal,
            'tax_total': tax_total,
            'grand_total': subtotal + tax_total
        }

    def proceed_payment_card_button_click(self, **event_args):
        """Handle proceeding to payment"""
        if not self.selected_customer or not self.bill_items:
            alert("Please select a customer and add at least one item to the bill.")
            return
            
        if not all('billing_item' in item for item in self.bill_items):
            alert("Please complete all billing items.")
            return
            
        try:
            action = "update" if hasattr(self, 'existing_invoice_id') else "create"
            if not confirm(f"This will {action} an invoice in QuickBooks Online. Continue?"):
                return
                
            # Create invoice in QBO
            result = anvil.server.call(
                'create_bill_with_items',
                self.bill_items,
                self.selected_customer,
                getattr(self, 'existing_invoice_id', None)
            )
            
            self.existing_invoice_id = result['qbo_invoice']['Id']
            
            # Ask user for payment method
            payment_choice = alert(
                message="How would you like to process this invoice?",
                title="Payment Method",
                buttons=["Record Credit/Debit Card", "Send as Invoice", "Cancel"],
                large=True
            )
            
            if payment_choice == "Record Credit/Debit Card":
                # Open card info form with invoice details
                open_form('cardInfo', 
                    invoice_id=self.existing_invoice_id,
                    amount=result['bill']['grandTotal'],  # Changed from grand_total to grandTotal
                    customer=self.selected_customer
                )
            elif payment_choice == "Send as Invoice":
                # For now, just show success message
                alert(f"Invoice {result['qbo_invoice']['Id']} will be sent to customer.")
            else:
                # User clicked Cancel
                alert("Invoice created but no payment method selected.")
            
        except Exception as e:
            print(f"Error processing bill: {str(e)}")
            alert(f"Failed to process bill: {str(e)}")
            
    def update_totals(self):
        """Update all total labels"""
        try:
            subtotal = 0
            tax_total = 0
            
            for item in self.bill_items:
                if not item or 'billing_item' not in item:
                    continue
                    
                quantity = int(item.get('quantity', 1))
                cost = item['billing_item']['mattsCost']
                subtotal += cost * quantity
                
                # Safely handle tax amount
                tax_amount = 0
                if item.get('tax_amount') is not None:
                    tax_amount = item['tax_amount']
                tax_total += tax_amount
                
            grand_total = subtotal + tax_total
            
            # Update labels with formatted amounts
            self.sub_total_label.text = f"${subtotal//100}.{subtotal%100:02d}"
            self.taxes_total_label.text = f"${tax_total//100}.{tax_total%100:02d}"
            self.bill_total_label.text = f"${grand_total//100}.{grand_total%100:02d}"
            
        except Exception as e:
            print(f"Error updating totals: {str(e)}")
            # Set default values if there's an error
            self.sub_total_label.text = "$0.00"
            self.taxes_total_label.text = "$0.00"
            self.bill_total_label.text = "$0.00"
