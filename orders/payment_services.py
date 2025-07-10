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


class StripePaymentService(PaymentService):
    """Handle Stripe payments for cards, PayPal, Apple Pay, Google Pay"""
    
    def process_payment(self, request, payment_method='card'):
        try:
            # Create line items for each product
            line_items = []
            for item in self.order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'ngn',
                        'product_data': {
                            'name': item.product.name,
                            'description': item.product.description[:100] if item.product.description else '',
                            'images': [request.build_absolute_uri(item.product.image.url)] if item.product.image else [],
                        },
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': item.quantity,
                })
            
            # Configure payment method types based on selection
            payment_method_types = ['card']
            if payment_method == 'paypal':
                payment_method_types = ['card', 'paypal']
            elif payment_method == 'apple_pay':
                payment_method_types = ['card', 'apple_pay']
            elif payment_method == 'google_pay':
                payment_method_types = ['card', 'google_pay']
            
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=payment_method_types,
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('orders:order_success', args=[self.order.id])),
                cancel_url=request.build_absolute_uri(reverse('cart:cart_detail')),
                metadata={
                    'order_id': self.order.id,
                    'user_id': request.user.id,
                    'payment_method': payment_method
                },
                customer_email=self.order.email,
                shipping_address_collection={'allowed_countries': ['NG']},
                allow_promotion_codes=True,
                billing_address_collection='required',
            )
            
            return {'success': True, 'redirect_url': stripe_session.url}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class PayPalPaymentService(PaymentService):
    """Handle PayPal payments"""
    
    def __init__(self, order):
        super().__init__(order)
        self.client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'your_paypal_client_id')
        self.client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', 'your_paypal_client_secret')
        self.base_url = "https://api-m.sandbox.paypal.com" if getattr(settings, 'PAYPAL_SANDBOX', True) else "https://api-m.paypal.com"
    
    def process_payment(self, request):
        """Process PayPal payment"""
        try:
            # For now, redirect to PayPal checkout via Stripe
            # In production, you would implement PayPal's API directly
            stripe_service = StripePaymentService(self.order)
            return stripe_service.process_payment(request, 'paypal')
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class FlutterwavePaymentService(PaymentService):
    """Handle Flutterwave payments"""
    
    def __init__(self, order):
        super().__init__(order)
        self.secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', 'your_flutterwave_secret_key')
        self.public_key = getattr(settings, 'FLUTTERWAVE_PUBLIC_KEY', 'your_flutterwave_public_key')
        self.base_url = "https://api.flutterwave.com/v3"
    
    def process_payment(self, request):
        """Process Flutterwave payment"""
        try:
            url = f"{self.base_url}/payments"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "tx_ref": f"ORDER-{self.order.id}",
                "amount": self.amount / 100,  # Flutterwave expects amount in Naira
                "currency": "NGN",
                "redirect_url": request.build_absolute_uri(reverse('orders:order_success', args=[self.order.id])),
                "customer": {
                    "email": self.order.email,
                    "name": f"{self.order.first_name} {self.order.last_name}",
                    "phone_number": self.order.phone
                },
                "customizations": {
                    "title": "KitchenCrate Payment",
                    "description": f"Payment for Order #{self.order.id}",
                    "logo": request.build_absolute_uri('/static/images/kitchencrae-logo.svg')
                },
                "meta": {
                    "order_id": self.order.id,
                    "user_id": request.user.id
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'success': True,
                    'redirect_url': data['data']['link'],
                    'reference': data['data']['tx_ref']
                }
            else:
                return {'success': False, 'error': data['message']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class PaystackPaymentService(PaymentService):
    """Handle Paystack payments"""
    
    def __init__(self, order):
        super().__init__(order)
        self.secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', 'your_paystack_secret_key')
        self.public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', 'your_paystack_public_key')
        self.base_url = "https://api.paystack.co"
    
    def initialize_payment(self, request):
        """Initialize Paystack payment"""
        try:
            url = f"{self.base_url}/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "email": self.order.email,
                "amount": self.amount,
                "currency": "NGN",
                "reference": f"ORDER-{self.order.id}",
                "callback_url": request.build_absolute_uri(reverse('orders:paystack_verify')),
                "metadata": {
                    "order_id": self.order.id,
                    "user_id": request.user.id,
                    "payment_method": "paystack"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if data['status']:
                return {
                    'success': True,
                    'authorization_url': data['data']['authorization_url'],
                    'reference': data['data']['reference']
                }
            else:
                return {'success': False, 'error': data['message']}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, reference):
        """Verify Paystack payment"""
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            headers = {
                "Authorization": f"Bearer {self.secret_key}"
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data['status'] and data['data']['status'] == 'success':
                return {
                    'success': True,
                    'amount': data['data']['amount'] / 100,
                    'reference': data['data']['reference']
                }
            else:
                return {'success': False, 'error': 'Payment verification failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class USSDPaymentService(PaymentService):
    """Handle USSD payments"""
    
    def __init__(self, order):
        super().__init__(order)
        self.ussd_codes = {
            'gtbank': '*737*1*{account}*{amount}#',
            'zenith': '*966*{account}*{amount}#',
            'access': '*901*{account}*{amount}#',
            'firstbank': '*894*{account}*{amount}#',
            'uba': '*919*{account}*{amount}#',
            'fidelity': '*770*{account}*{amount}#',
            'ecobank': '*326*{account}*{amount}#',
            'stanbic': '*909*{account}*{amount}#',
            'union': '*826*{account}*{amount}#',
            'wema': '*945*{account}*{amount}#',
        }
    
    def generate_ussd_code(self, bank_code, account_number):
        """Generate USSD code for payment"""
        if bank_code in self.ussd_codes:
            ussd_template = self.ussd_codes[bank_code]
            return ussd_template.format(
                account=account_number,
                amount=self.amount
            )
        return None
    
    def get_payment_instructions(self):
        """Get USSD payment instructions"""
        return {
            'amount': self.amount / 100,
            'reference': f"ORDER-{self.order.id}",
            'instructions': [
                "Dial the USSD code for your bank",
                "Enter your PIN when prompted",
                "Confirm the payment amount",
                "Use the reference number provided",
                "Keep the transaction receipt"
            ]
        }


class MobileMoneyPaymentService(PaymentService):
    """Handle Mobile Money payments"""
    
    def __init__(self, order):
        super().__init__(order)
        self.providers = {
            'paga': {
                'name': 'Paga',
                'code': '*242*1*{phone}*{amount}#',
                'instructions': 'Dial *242*1*{phone}*{amount}# to pay with Paga',
                'color': '#00A651',
                'logo': 'fas fa-mobile-alt'
            },
            'opay': {
                'name': 'OPay',
                'code': '*955*{phone}*{amount}#',
                'instructions': 'Dial *955*{phone}*{amount}# to pay with OPay',
                'color': '#FF6B35',
                'logo': 'fas fa-wallet'
            },
            'airtel_money': {
                'name': 'Airtel Money',
                'code': '*432*{phone}*{amount}#',
                'instructions': 'Dial *432*{phone}*{amount}# to pay with Airtel Money',
                'color': '#FF0000',
                'logo': 'fas fa-mobile-alt'
            },
            'mtn_momo': {
                'name': 'MTN MoMo',
                'code': '*165*{phone}*{amount}#',
                'instructions': 'Dial *165*{phone}*{amount}# to pay with MTN MoMo',
                'color': '#FFC107',
                'logo': 'fas fa-mobile-alt'
            },
            'vodafone_cash': {
                'name': 'Vodafone Cash',
                'code': '*110*{phone}*{amount}#',
                'instructions': 'Dial *110*{phone}*{amount}# to pay with Vodafone Cash',
                'color': '#E60000',
                'logo': 'fas fa-mobile-alt'
            }
        }
    
    def generate_payment_code(self, provider, phone_number):
        """Generate mobile money payment code"""
        if provider in self.providers:
            provider_info = self.providers[provider]
            return provider_info['code'].format(
                phone=phone_number,
                amount=self.amount
            )
        return None
    
    def get_provider_instructions(self, provider):
        """Get instructions for specific provider"""
        if provider in self.providers:
            return self.providers[provider]
        return None


def get_payment_service(order, payment_method):
    """Factory function to get appropriate payment service"""
    if payment_method == 'paystack':
        return PaystackPaymentService(order)
    elif payment_method == 'paypal':
        return PayPalPaymentService(order)
    elif payment_method == 'flutterwave':
        return FlutterwavePaymentService(order)
    elif payment_method == 'ussd':
        return USSDPaymentService(order)
    elif payment_method == 'mobile_money':
        return MobileMoneyPaymentService(order)
    else:
        return StripePaymentService(order) 