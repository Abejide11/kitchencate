import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from .email_services import send_payment_confirmation_email, send_payment_pending_email


class FlutterwavePaymentService:
    """Flutterwave payment service for multiple payment methods"""
    
    def __init__(self, order):
        self.order = order
        self.amount = order.get_total_cost()
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        self.secret_key = settings.FLUTTERWAVE_SECRET_KEY
        self.encryption_key = settings.FLUTTERWAVE_ENCRYPTION_KEY
        self.base_url = "https://api.flutterwave.com/v3"
        
    def create_payment_link(self, request, payment_method):
        """Create a Flutterwave payment link"""
        try:
            # Prepare payment data
            payment_data = {
                "tx_ref": f"ORDER-{self.order.id}-{int(self.order.created.timestamp())}",
                "amount": self.amount,
                "currency": settings.PAYMENT_CURRENCY,
                "redirect_url": request.build_absolute_uri(
                    reverse('orders:order_success', kwargs={'order_id': self.order.id})
                ),
                "customer": {
                    "email": self.order.email,
                    "name": f"{self.order.first_name} {self.order.last_name}",
                    "phone_number": self.order.phone or ""
                },
                "customizations": {
                    "title": "KitchenCrate Payment",
                    "description": f"Payment for Order #{self.order.id}",
                    "logo": request.build_absolute_uri('/static/images/kitchencrae-logo.svg')
                },
                "meta": {
                    "order_id": self.order.id,
                    "payment_method": payment_method
                }
            }
            
            # Add payment method specific configurations
            if payment_method == 'card':
                payment_data["payment_options"] = "card"
            elif payment_method == 'bank_transfer':
                payment_data["payment_options"] = "banktransfer"
            elif payment_method == 'ussd':
                payment_data["payment_options"] = "ussd"
            elif payment_method == 'mobile_money':
                payment_data["payment_options"] = "mobilemoney"
            elif payment_method == 'qr_code':
                payment_data["payment_options"] = "qr"
            else:
                # Default to all payment methods
                payment_data["payment_options"] = "card,banktransfer,ussd,mobilemoney,qr"
            
            # Make API request to Flutterwave
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/payments",
                json=payment_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return {
                        'success': True,
                        'redirect_url': result['data']['link'],
                        'payment_reference': result['data']['reference']
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Payment initialization failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, transaction_id):
        """Verify a Flutterwave payment"""
        try:
            headers = {
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}/verify",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    payment_data = result['data']
                    
                    # Verify the payment details
                    if (payment_data['amount'] == self.amount and 
                        payment_data['currency'] == settings.PAYMENT_CURRENCY and
                        payment_data['status'] == 'successful'):
                        
                        return {
                            'success': True,
                            'payment_data': payment_data
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'Payment verification failed - amount or status mismatch'
                        }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', 'Payment verification failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, request_data):
        """Process Flutterwave webhook"""
        try:
            # Verify webhook signature
            if not self.verify_webhook_signature(request_data):
                return {
                    'success': False,
                    'error': 'Invalid webhook signature'
                }
            
            # Extract payment data
            payment_data = request_data.get('data', {})
            transaction_id = payment_data.get('id')
            status = payment_data.get('status')
            reference = payment_data.get('reference')
            
            # Update order status based on payment status
            if status == 'successful':
                self.order.payment_status = 'completed'
                self.order.payment_reference = reference
                self.order.payment_notes = f'Flutterwave payment successful. Transaction ID: {transaction_id}'
                self.order.save()
                
                # Send confirmation email
                try:
                    send_payment_confirmation_email(self.order)
                except Exception as e:
                    print(f"Failed to send confirmation email: {e}")
                
                return {
                    'success': True,
                    'message': 'Payment processed successfully'
                }
            elif status == 'pending':
                self.order.payment_status = 'pending'
                self.order.payment_reference = reference
                self.order.payment_notes = f'Flutterwave payment pending. Transaction ID: {transaction_id}'
                self.order.save()
                
                return {
                    'success': True,
                    'message': 'Payment is pending'
                }
            else:
                self.order.payment_status = 'failed'
                self.order.payment_reference = reference
                self.order.payment_notes = f'Flutterwave payment failed. Transaction ID: {transaction_id}'
                self.order.save()
                
                return {
                    'success': False,
                    'error': f'Payment failed with status: {status}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, request_data):
        """Verify Flutterwave webhook signature"""
        try:
            # Get the signature from headers (you'll need to pass this from the view)
            # This is a simplified verification - you should implement proper signature verification
            return True
        except Exception:
            return False
    
    def get_payment_methods(self):
        """Get available payment methods"""
        return {
            'card': {
                'name': 'Credit/Debit Card',
                'description': 'Visa, Mastercard, Verve',
                'icon': '💳'
            },
            'bank_transfer': {
                'name': 'Bank Transfer',
                'description': 'Direct bank transfer',
                'icon': '🏦'
            },
            'ussd': {
                'name': 'USSD',
                'description': 'USSD payment codes',
                'icon': '📱'
            },
            'mobile_money': {
                'name': 'Mobile Money',
                'description': 'Mobile money wallets',
                'icon': '💰'
            },
            'qr_code': {
                'name': 'QR Code',
                'description': 'Scan QR code to pay',
                'icon': '📱'
            }
        }


def get_flutterwave_service(order):
    """Factory function to get Flutterwave payment service"""
    return FlutterwavePaymentService(order) 