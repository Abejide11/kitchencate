# Generated by Django 4.2.7 on 2025-07-10 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_refund_amount_order_refund_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_id',
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('ussd', 'USSD Payment'), ('mobile_money', 'Mobile Money'), ('flutterwave_card', 'Flutterwave Card'), ('flutterwave_bank', 'Flutterwave Bank Transfer'), ('flutterwave_ussd', 'Flutterwave USSD'), ('flutterwave_mobile', 'Flutterwave Mobile Money'), ('flutterwave_qr', 'Flutterwave QR Code')], default='flutterwave_card', max_length=20),
        ),
    ]
