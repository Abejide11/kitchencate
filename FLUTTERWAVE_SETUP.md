# 🚀 Flutterwave Payment Integration Setup Guide

This guide will help you set up Flutterwave payment integration for your Django e-commerce project. **This project now uses Flutterwave exclusively for all payment processing.**

## 📋 Prerequisites

1. **Flutterwave Account**: Sign up at [Flutterwave Dashboard](https://dashboard.flutterwave.com/)
2. **Django Project**: Your e-commerce project should be running
3. **Domain**: A live domain for webhook URLs (or localhost for testing)

## 🔑 Step 1: Get Your Flutterwave API Keys

### 1.1 Create Flutterwave Account
- Go to [Flutterwave Dashboard](https://dashboard.flutterwave.com/)
- Sign up for a new account
- Complete your business verification

### 1.2 Get API Keys
- Navigate to **Settings → API Keys** in your Flutterwave Dashboard
- Copy your **Public Key** (starts with `FLWPUBK_`)
- Copy your **Secret Key** (starts with `FLWSECK_`)
- Copy your **Encryption Key** (for additional security)

## 🔧 Step 2: Configure Environment Variables

### 2.1 Create/Update `.env` File
Add these variables to your `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
EMAIL_HOST_USER=webblog902@gmail.com
EMAIL_HOST_PASSWORD=ercupdkazeiprbzc

# Flutterwave Configuration (REQUIRED)
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST_your_actual_public_key_here
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST_your_actual_secret_key_here
FLUTTERWAVE_ENCRYPTION_KEY=your_actual_encryption_key_here
FLUTTERWAVE_WEBHOOK_SECRET=your_webhook_secret_here
```

### 2.2 Replace Placeholder Values
- Replace `FLWPUBK_TEST_your_actual_public_key_here` with your actual public key
- Replace `FLWSECK_TEST_your_actual_secret_key_here` with your actual secret key
- Replace `your_actual_encryption_key_here` with your encryption key
- Replace `your_webhook_secret_here` with a secure webhook secret

## 🌐 Step 3: Set Up Webhooks

### 3.1 Configure Webhook URL
- Go to **Settings → Webhooks** in your Flutterwave Dashboard
- Add a new webhook endpoint:
  - **URL**: `https://yourdomain.com/orders/webhook/flutterwave/`
  - **Events**: Select all payment events (charge.completed, charge.failed, etc.)

### 3.2 Test Webhook
- Use the webhook testing tool in Flutterwave Dashboard
- Verify that your Django app receives webhook notifications

## 🧪 Step 4: Test the Integration

### 4.1 Run Setup Command
```bash
python manage.py setup_payments
```

### 4.2 Check Payment Methods
The command should show:
- ✅ Flutterwave Card
- ✅ Flutterwave Bank Transfer  
- ✅ Flutterwave USSD
- ✅ Flutterwave Mobile Money
- ✅ Flutterwave QR Code

### 4.3 Test Payment Flow
1. Add items to cart
2. Go to checkout
3. Select a Flutterwave payment method
4. Complete the payment
5. Verify webhook processing

## 💳 Available Payment Methods

### Flutterwave Card
- **Supported Cards**: Visa, Mastercard, Verve
- **Countries**: Nigeria, Ghana, Kenya, South Africa, and more
- **Processing Time**: Instant

### Flutterwave Bank Transfer
- **Supported Banks**: All major Nigerian banks
- **Processing Time**: 1-3 business days
- **Features**: Automatic verification

### Flutterwave USSD
- **Supported Networks**: MTN, Airtel, Glo, 9mobile
- **Processing Time**: Instant
- **Features**: No internet required

### Flutterwave Mobile Money
- **Supported Providers**: M-Pesa, MTN MoMo, Airtel Money, etc.
- **Processing Time**: Instant
- **Features**: Mobile wallet integration

### Flutterwave QR Code
- **Supported Apps**: Flutterwave Pay, banking apps
- **Processing Time**: Instant
- **Features**: Contactless payment

## 🔒 Security Features

### Webhook Verification
- All webhooks are verified using Flutterwave's signature
- Invalid webhooks are rejected automatically
- Payment status is updated securely

### Encryption
- All sensitive data is encrypted
- API keys are stored securely in environment variables
- HTTPS is required for production

## 📧 Email Notifications

The system automatically sends:
- **Payment Confirmation**: When payment is successful
- **Payment Pending**: When payment is initiated
- **Payment Failed**: When payment fails

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Flutterwave payment processing is not configured"
**Solution**: Check your `.env` file and ensure all Flutterwave keys are set correctly.

#### 2. "Invalid webhook signature"
**Solution**: Verify your webhook secret in the Flutterwave Dashboard.

#### 3. "Payment verification failed"
**Solution**: Check that the payment amount and currency match your order.

#### 4. Webhook not receiving notifications
**Solution**: 
- Verify webhook URL is accessible
- Check firewall settings
- Ensure HTTPS is used in production

### Debug Commands

```bash
# Check Flutterwave configuration
python manage.py setup_payments --check-flutterwave

# Test Flutterwave connection
python manage.py setup_payments --test-flutterwave
```

## 📱 Mobile Optimization

All Flutterwave payment methods are mobile-optimized:
- Responsive design for all screen sizes
- Touch-friendly payment buttons
- Mobile-optimized payment forms
- USSD codes for feature phones

## 🌍 Multi-Country Support

Flutterwave supports payments from:
- **Nigeria**: All major banks and mobile money
- **Ghana**: Mobile money and cards
- **Kenya**: M-Pesa and cards
- **South Africa**: Cards and EFT
- **Uganda**: Mobile money and cards
- **And more**: Check Flutterwave documentation

## 📊 Analytics & Reporting

Track your payments with:
- **Flutterwave Dashboard**: Real-time payment analytics
- **Django Admin**: Order and payment management
- **Email Reports**: Automated payment summaries

## 🚀 Going Live

### 1. Switch to Live Keys
- Replace test keys with live keys in `.env`
- Update webhook URLs to production domain
- Test with small amounts first

### 2. Enable Additional Features
- **Recurring Payments**: For subscriptions
- **Split Payments**: For marketplaces
- **International Payments**: For cross-border transactions

### 3. Compliance
- Ensure PCI DSS compliance
- Follow local payment regulations
- Implement proper error handling

## 📞 Support

- **Flutterwave Support**: [support@flutterwave.com](mailto:support@flutterwave.com)
- **Documentation**: [Flutterwave Docs](https://developer.flutterwave.com/)
- **API Reference**: [Flutterwave API](https://developer.flutterwave.com/reference)

---

## ✅ Checklist

- [ ] Flutterwave account created
- [ ] API keys obtained
- [ ] Environment variables configured
- [ ] Webhook URL set up
- [ ] Payment methods tested
- [ ] Email notifications working
- [ ] Mobile optimization verified
- [ ] Security measures implemented
- [ ] Live keys configured (for production)
- [ ] Compliance requirements met

Your Flutterwave integration is now ready! 🎉

---

## 🔄 Migration from Stripe

**Note**: This project has been migrated from Stripe to Flutterwave. All Stripe-related code has been removed and replaced with Flutterwave integration. The payment system now exclusively uses Flutterwave for all payment processing. 