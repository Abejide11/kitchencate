import stripe
from django.conf import settings
from django.urls import reverse

class StripePaymentService:
    def __init__(self, order):
        self.order = order
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def process_payment(self, request):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'ngn',
                    'product_data': {
                        'name': f'Order #{self.order.id}',
                    },
                    'unit_amount': int(self.order.get_total_cost() * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('orders:order_success', args=[self.order.id])),
            cancel_url=request.build_absolute_uri(reverse('orders:order_create')),
            customer_email=self.order.email,
            metadata={'order_id': self.order.id}
        )
        return {'success': True, 'redirect_url': session.url, 'payment_reference': session.id}


def get_payment_service(order, payment_method=None):
    return StripePaymentService(order) 