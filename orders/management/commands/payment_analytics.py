from django.core.management.base import BaseCommand
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, BankTransferDetails
from store.models import Product


class Command(BaseCommand):
    help = 'Generate payment analytics and reports for KitchenCrate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format (default: text)'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_format = options['format']
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Generating payment analytics for the last {days} days...')
        )
        
        # Get analytics data
        analytics = self.get_analytics(start_date, end_date)
        
        # Output based on format
        if output_format == 'json':
            self.output_json(analytics)
        elif output_format == 'csv':
            self.output_csv(analytics)
        else:
            self.output_text(analytics)

    def get_analytics(self, start_date, end_date):
        """Generate comprehensive analytics data"""
        
        # Order statistics
        orders = Order.objects.filter(created__range=(start_date, end_date))
        total_orders = orders.count()
        
        # Calculate total revenue by summing order items
        total_revenue = sum(order.get_total_cost() for order in orders)
        
        # Payment method breakdown
        payment_methods = []
        for method in orders.values('payment_method').distinct():
            method_orders = orders.filter(payment_method=method['payment_method'])
            revenue = sum(order.get_total_cost() for order in method_orders)
            payment_methods.append({
                'payment_method': method['payment_method'],
                'count': method_orders.count(),
                'revenue': revenue
            })
        payment_methods.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Payment status breakdown
        payment_statuses = []
        for status in orders.values('payment_status').distinct():
            status_orders = orders.filter(payment_status=status['payment_status'])
            revenue = sum(order.get_total_cost() for order in status_orders)
            payment_statuses.append({
                'payment_status': status['payment_status'],
                'count': status_orders.count(),
                'revenue': revenue
            })
        payment_statuses.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Order status breakdown
        order_statuses = []
        for status in orders.values('status').distinct():
            status_orders = orders.filter(status=status['status'])
            revenue = sum(order.get_total_cost() for order in status_orders)
            order_statuses.append({
                'status': status['status'],
                'count': status_orders.count(),
                'revenue': revenue
            })
        order_statuses.sort(key=lambda x: x['revenue'], reverse=True)
        
        # Daily revenue trend
        daily_revenue = []
        from django.db.models import DateField
        from django.db.models.functions import TruncDate
        
        daily_orders = orders.annotate(day=TruncDate('created')).values('day').distinct()
        for day_data in daily_orders:
            day_orders = orders.filter(created__date=day_data['day'])
            revenue = sum(order.get_total_cost() for order in day_orders)
            daily_revenue.append({
                'day': day_data['day'],
                'revenue': revenue,
                'orders': day_orders.count()
            })
        daily_revenue.sort(key=lambda x: x['day'])
        
        # Bank transfer analytics
        bank_transfers = BankTransferDetails.objects.filter(
            created__range=(start_date, end_date)
        )
        bank_transfer_stats = {
            'total_transfers': bank_transfers.count(),
            'verified_transfers': bank_transfers.filter(verified=True).count(),
            'pending_transfers': bank_transfers.filter(verified=False).count(),
            'total_amount': bank_transfers.aggregate(total=Sum('transfer_amount'))['total'] or 0,
            'verified_amount': bank_transfers.filter(verified=True).aggregate(total=Sum('transfer_amount'))['total'] or 0,
        }
        
        # Bank breakdown
        bank_breakdown = []
        for bank in bank_transfers.values('bank_name').distinct():
            bank_transfers_filtered = bank_transfers.filter(bank_name=bank['bank_name'])
            amount = bank_transfers_filtered.aggregate(total=Sum('transfer_amount'))['total'] or 0
            verified_count = bank_transfers_filtered.filter(verified=True).count()
            bank_breakdown.append({
                'bank_name': bank['bank_name'],
                'count': bank_transfers_filtered.count(),
                'amount': amount,
                'verified_count': verified_count
            })
        bank_breakdown.sort(key=lambda x: x['amount'], reverse=True)
        
        # Top products by revenue
        top_products = Product.objects.filter(
            order_items__order__created__range=(start_date, end_date)
        ).annotate(
            total_sold=Sum('order_items__quantity'),
            total_revenue=Sum('order_items__price')
        ).order_by('-total_revenue')[:10]
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': (end_date - start_date).days
            },
            'overview': {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'average_order_value': total_revenue / total_orders if total_orders > 0 else 0,
                'orders_per_day': total_orders / (end_date - start_date).days if (end_date - start_date).days > 0 else 0
            },
            'payment_methods': list(payment_methods),
            'payment_statuses': list(payment_statuses),
            'order_statuses': list(order_statuses),
            'daily_revenue': list(daily_revenue),
            'bank_transfers': bank_transfer_stats,
            'bank_breakdown': list(bank_breakdown),
            'top_products': [
                {
                    'name': product.name,
                    'total_sold': product.total_sold or 0,
                    'total_revenue': product.total_revenue or 0
                }
                for product in top_products
            ]
        }

    def output_text(self, analytics):
        """Output analytics in text format"""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('KITCHENCRATE PAYMENT ANALYTICS REPORT')
        self.stdout.write('='*60)
        
        # Period
        period = analytics['period']
        self.stdout.write(f"\nPeriod: {period['start_date'].strftime('%Y-%m-%d')} to {period['end_date'].strftime('%Y-%m-%d')} ({period['days']} days)")
        
        # Overview
        overview = analytics['overview']
        self.stdout.write('\n📊 OVERVIEW')
        self.stdout.write('-' * 30)
        self.stdout.write(f"Total Orders: {overview['total_orders']:,}")
        self.stdout.write(f"Total Revenue: ₦{overview['total_revenue']:,.2f}")
        self.stdout.write(f"Average Order Value: ₦{overview['average_order_value']:,.2f}")
        self.stdout.write(f"Orders per Day: {overview['orders_per_day']:.1f}")
        
        # Payment Methods
        self.stdout.write('\n💳 PAYMENT METHODS')
        self.stdout.write('-' * 30)
        for method in analytics['payment_methods']:
            percentage = (method['count'] / overview['total_orders'] * 100) if overview['total_orders'] > 0 else 0
            self.stdout.write(
                f"{method['payment_method'].title()}: {method['count']} orders "
                f"(₦{method['revenue']:,.2f}) - {percentage:.1f}%"
            )
        
        # Payment Status
        self.stdout.write('\n✅ PAYMENT STATUS')
        self.stdout.write('-' * 30)
        for status in analytics['payment_statuses']:
            percentage = (status['count'] / overview['total_orders'] * 100) if overview['total_orders'] > 0 else 0
            self.stdout.write(
                f"{status['payment_status'].title()}: {status['count']} orders "
                f"(₦{status['revenue']:,.2f}) - {percentage:.1f}%"
            )
        
        # Bank Transfers
        bank_transfers = analytics['bank_transfers']
        if bank_transfers['total_transfers'] > 0:
            self.stdout.write('\n🏦 BANK TRANSFERS')
            self.stdout.write('-' * 30)
            self.stdout.write(f"Total Transfers: {bank_transfers['total_transfers']}")
            self.stdout.write(f"Verified: {bank_transfers['verified_transfers']} (₦{bank_transfers['verified_amount']:,.2f})")
            self.stdout.write(f"Pending: {bank_transfers['pending_transfers']}")
            self.stdout.write(f"Total Amount: ₦{bank_transfers['total_amount']:,.2f}")
            
            # Bank breakdown
            self.stdout.write('\nBank Breakdown:')
            for bank in analytics['bank_breakdown']:
                verification_rate = (bank['verified_count'] / bank['count'] * 100) if bank['count'] > 0 else 0
                self.stdout.write(
                    f"  {bank['bank_name']}: {bank['count']} transfers "
                    f"(₦{bank['amount']:,.2f}) - {verification_rate:.1f}% verified"
                )
        
        # Top Products
        if analytics['top_products']:
            self.stdout.write('\n🏆 TOP PRODUCTS BY REVENUE')
            self.stdout.write('-' * 30)
            for i, product in enumerate(analytics['top_products'], 1):
                self.stdout.write(
                    f"{i}. {product['name']}: {product['total_sold']} sold "
                    f"(₦{product['total_revenue']:,.2f})"
                )
        
        # Daily Revenue Trend
        if analytics['daily_revenue']:
            self.stdout.write('\n📈 DAILY REVENUE TREND (Last 7 days)')
            self.stdout.write('-' * 30)
            for day_data in analytics['daily_revenue'][-7:]:
                self.stdout.write(
                    f"{day_data['day']}: ₦{day_data['revenue']:,.2f} "
                    f"({day_data['orders']} orders)"
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Report generated successfully!')
        self.stdout.write('='*60)

    def output_json(self, analytics):
        """Output analytics in JSON format"""
        import json
        self.stdout.write(json.dumps(analytics, indent=2, default=str))

    def output_csv(self, analytics):
        """Output analytics in CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write overview
        writer.writerow(['Metric', 'Value'])
        overview = analytics['overview']
        writer.writerow(['Total Orders', overview['total_orders']])
        writer.writerow(['Total Revenue', overview['total_revenue']])
        writer.writerow(['Average Order Value', overview['average_order_value']])
        writer.writerow(['Orders per Day', overview['orders_per_day']])
        
        # Write payment methods
        writer.writerow([])
        writer.writerow(['Payment Method', 'Orders', 'Revenue', 'Percentage'])
        for method in analytics['payment_methods']:
            percentage = (method['count'] / overview['total_orders'] * 100) if overview['total_orders'] > 0 else 0
            writer.writerow([
                method['payment_method'],
                method['count'],
                method['revenue'],
                f"{percentage:.1f}%"
            ])
        
        # Write payment statuses
        writer.writerow([])
        writer.writerow(['Payment Status', 'Orders', 'Revenue', 'Percentage'])
        for status in analytics['payment_statuses']:
            percentage = (status['count'] / overview['total_orders'] * 100) if overview['total_orders'] > 0 else 0
            writer.writerow([
                status['payment_status'],
                status['count'],
                status['revenue'],
                f"{percentage:.1f}%"
            ])
        
        self.stdout.write(output.getvalue()) 