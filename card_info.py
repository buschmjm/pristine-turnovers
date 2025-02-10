from datetime import datetime  # Ensure this is at the very top, before any other imports
from anvil import *
import anvil.server

class cardInfo(CardInfoTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.setup_initial_values()
        
        # Set up event handlers with the exact names expected by the form designer
        if hasattr(self, 'card_number_label'):
            self.card_number_label.set_event_handler('pressed_enter', self.card_number_label_pressed_enter)
        if hasattr(self, 'process_payment_button'):
            self.process_payment_button.set_event_handler('click', self.process_payment_button_click)
    
    def setup_initial_values(self):
        self.subtotal = 0.0
        self.total = 0.0
        self.bill_items = []
    
    def card_number_label_pressed_enter(self, **event_args):
        """This matches the exact name expected in the form designer"""
        try:
            if hasattr(self, 'cvc_label'):
                self.cvc_label.focus()
        except Exception as e:
            print(f"Error in card number enter: {str(e)}")
    
    def process_payment_button_click(self, **event_args):
        """This matches the exact name expected in the form designer"""
        try:
            # Ensure we have the datetime module imported
            current_time = datetime.now()
            
            payment_data = {
                'timestamp': current_time,
                'card_number': self.card_number_label.text if hasattr(self, 'card_number_label') else None,
                'cvc': self.cvc_label.text if hasattr(self, 'cvc_label') else None,
                'amount': getattr(self, 'total', 0)
            }
            
            if not all([payment_data['card_number'], payment_data['cvc'], payment_data['amount']]):
                raise ValueError("Please fill in all required payment information")
                
            result = anvil.server.call('process_payment', payment_data)
            alert("Payment processed successfully!")
        except Exception as e:
            alert(f"Payment processing error: {str(e)}")

    def update_totals(self, bill_items):
        """Update totals from bill items"""
        try:
            if not bill_items or not isinstance(bill_items, list):
                self.subtotal = 0.0
                self.total = 0.0
                return
                
            valid_items = [
                item for item in bill_items 
                if item and isinstance(item, dict) and 'amount' in item 
                and item['amount'] is not None
            ]
            
            self.subtotal = sum(float(item['amount']) for item in valid_items)
            self.total = self.subtotal  # Add tax calculation if needed
            
            # Update UI labels if they exist
            if hasattr(self, 'subtotal_label'):
                self.subtotal_label.text = f"${self.subtotal:.2f}"
            if hasattr(self, 'total_label'):
                self.total_label.text = f"${self.total:.2f}"
                
        except Exception as e:
            print(f"Error updating totals: {str(e)}")
            self.subtotal = 0.0
            self.total = 0.0

    def refresh_bill_items(self):
        """Refresh bill items and update totals"""
        try:
            self.bill_items = anvil.server.call('get_bill_items') or []
            self.update_totals(self.bill_items)
        except Exception as e:
            print(f"Error refreshing bill items: {str(e)}")
            self.bill_items = []
            self.update_totals([])
