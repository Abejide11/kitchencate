import requests
import json
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from .flutterwave_services import get_flutterwave_service


class FlutterwavePaymentService:
    """Flutterwave payment service wrapper"""
    
    def __init__(self, order):
        self.flutterwave_service = get_flutterwave_service(order)
    
    def process_payment(self, request, payment_method):
        """Process payment with Flutterwave"""
        return self.flutterwave_service.create_payment_link(request, payment_method)


class PaymentService:
    """Base payment service class for local payment methods"""
    
    def __init__(self, order):
        self.order = order
        self.amount = int(order.get_total_cost() * 100)  # Convert to kobo
        self.providers = [
            {'code': 'paga', 'name': 'Paga', 'ussd': '*242*1*'},
            {'code': 'opay', 'name': 'OPay', 'ussd': '*955*'},
            {'code': 'airtel_money', 'name': 'Airtel Money', 'ussd': '*432*'},
            {'code': 'mtn_momo', 'name': 'MTN Mobile Money', 'ussd': '*600*'},
            {'code': 'vodafone_cash', 'name': 'Vodafone Cash', 'ussd': '*110*'}
        ]
    
    def process_payment(self, request, payment_method):
        """Process payment - to be implemented by subclasses"""
        raise NotImplementedError
    
    def generate_ussd_code(self, bank_code, account_number):
        """Generate USSD code for payment"""
        # This is a placeholder implementation
        # In a real implementation, you would integrate with actual USSD service
        return f"*{bank_code}*{account_number}*{self.order.get_total_cost()}#"
    
    def generate_payment_code(self, provider, phone_number):
        """Generate payment code for mobile money"""
        # This is a placeholder implementation
        # In a real implementation, you would integrate with actual mobile money service
        provider_codes = {
            'paga': '*242*1*',
            'opay': '*955*',
            'airtel_money': '*432*',
            'mtn_momo': '*600*',
            'vodafone_cash': '*110*'
        }
        
        code = provider_codes.get(provider, '*123*')
        return f"{code}{phone_number}*{self.order.get_total_cost()}#"
    
    def get_payment_instructions(self):
        """Get payment instructions"""
        return {
            'amount': self.order.get_total_cost(),
            'reference': f"ORDER-{self.order.id}",
            'instructions': [
                'Dial the USSD code provided',
                f'Confirm amount: ₦{self.order.get_total_cost()}',
                f'Use reference: ORDER-{self.order.id}',
                'Keep the transaction receipt'
            ]
        }


def get_payment_service(order, payment_method=None):
    """
    Factory function to get the appropriate payment service based on payment_method.
    """
    if payment_method.startswith('flutterwave_'):
        return FlutterwavePaymentService(order)
    else:
        return PaymentService(order) 