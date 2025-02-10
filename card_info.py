from datetime import datetime
from anvil import *
import anvil.server

class cardInfo(CardInfoTemplate):  # Make sure this matches your template name exactly
    def __init__(self, **properties):
        self.init_components(**properties)
        self.subtotal = 0
        self.total = 0
        self.bill_items = []
        # Set up event handlers in init
        if hasattr(self, 'card_number_label'):
            self.card_number_label.set_event_handler('pressed_enter', self.card_number_label_pressed_enter)
        if hasattr(self, 'process_payment_button'):
            self.process_payment_button.set_event_handler('click', self.process_payment_button_click)
    
    def card_number_label_pressed_enter(self, **event_args):
        """Handle enter key press on card number field"""
        self.cvc_label.focus()
        
    def process_payment_button_click(self, **event_args):
        """Handle payment processing"""
        try:
            current_time = datetime.now()
            # Add your payment processing logic here
            payment_data = {
                'timestamp': current_time,
                'card_number': self.card_number_label.text,
                'cvc': self.cvc_label.text,
                'amount': self.total
            }
            result = anvil.server.call('process_payment', payment_data)
            alert("Payment processed successfully!")
        except Exception as e:
            alert(f"Payment processing error: {str(e)}")
            
    def update_totals(self, bill_items):
        """Update totals from bill items"""
        try:
            if not bill_items:
                self.subtotal = 0
                self.total = 0
                return
                
            # Filter out None and invalid items
            valid_items = [item for item in bill_items if item and isinstance(item, dict) and 'amount' in item]
            
            if not valid_items:
                self.subtotal = 0
                self.total = 0
                return
                
            self.subtotal = sum(float(item['amount']) for item in valid_items)
            self.total = self.subtotal
            
            # Update labels if they exist
            if hasattr(self, 'subtotal_label'):
                self.subtotal_label.text = f"${self.subtotal:.2f}"
            if hasattr(self, 'total_label'):
                self.total_label.text = f"${self.total:.2f}"
                
        except Exception as e:
            print(f"Error in update_totals: {str(e)}")
            self.subtotal = 0
            self.total = 0

    def refresh_bill_items(self):
        """Refresh the bill items display"""
        try:
            self.bill_items = anvil.server.call('get_bill_items')
            self.update_totals(self.bill_items)
        except Exception as e:
            print(f"Error refreshing bill items: {str(e)}")
            self.bill_items = []
            self.update_totals([])
