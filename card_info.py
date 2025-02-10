from datetime import datetime

class cardInfo:
    def __init__(self, **properties):
        self.init_components(**properties)
        self.set_event_handlers()
        
    def set_event_handlers(self):
        """Set up event handlers for the form"""
        if hasattr(self, 'card_number_label'):
            self.card_number_label.set_event_handler('pressed_enter', self.card_number_label_pressed_enter)
        if hasattr(self, 'process_payment_button'):
            self.process_payment_button.set_event_handler('click', self.process_payment_button_click)
    
    def card_number_label_pressed_enter(self, **event_args):
        """Handle enter key press on card number field"""
        # Move focus to the next field
        self.cvc_label.focus()
        
    def process_payment_button_click(self, **event_args):
        """Handle payment processing"""
        try:
            # Get the current datetime for the transaction
            transaction_date = datetime.now()
            # Add your payment processing logic here
            # Example:
            # result = anvil.server.call('process_payment', self.card_number, self.cvc, transaction_date)
            pass
        except Exception as e:
            alert(f"Payment processing error: {str(e)}")

    def update_totals(self, bill_items):
        """Update totals from bill items"""
        if not bill_items:
            self.subtotal = 0
            self.total = 0
            return
            
        try:
            self.subtotal = sum(item['amount'] for item in bill_items if item and 'amount' in item)
            self.total = self.subtotal  # Add tax calculation if needed
        except (TypeError, KeyError) as e:
            print(f"Error calculating totals: {str(e)}")
            self.subtotal = 0
            self.total = 0

    # ...existing code...
