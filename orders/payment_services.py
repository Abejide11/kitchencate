import requests
import json
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Base payment service class"""
    
    def __init__(self, order):
        self.order = order
        self.amount = int(order.get_total_cost() * 100)  # Convert to kobo
    
    def process_payment(self, request):
        """Process payment - to be implemented by subclasses"""
        raise NotImplementedError 


def get_payment_service(order, payment_method=None):
    """
    Factory function to get the appropriate payment service based on payment_method.
    For now, only PaymentService is implemented. Extend this as needed.
    """
    # Example: if payment_method == 'stripe': return StripePaymentService(order)
    return PaymentService(order) 