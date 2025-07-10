# Payment System Setup Guide

## Overview
Your e-commerce system now supports multiple payment methods. This guide will help you configure each payment method properly.

## Payment Methods Available

### 1. Credit/Debit Card (Stripe)
- **Status**: ✅ Ready
- **Cards Supported**: Visa, Mastercard, American Express
- **Setup Required**: Stripe API Keys

### 2. Apple Pay
- **Status**: ✅ Ready (via Stripe)
- **Setup Required**: Stripe API Keys + Apple Pay Domain Verification

### 3. Google Pay
- **Status**: ✅ Ready (via Stripe)
- **Setup Required**: Stripe API Keys

### 4. Bank Transfer
- **Status**: ✅ Ready
- **Setup Required**: Bank account details for manual verification

### 5. USSD Payment
- **Status**: ⚠️ Placeholder (needs real USSD integration)
- **Setup Required**: USSD service provider integration

### 6. Mobile Money
- **Status**: ⚠️ Placeholder (needs real mobile money integration)
- **Setup Required**: Mobile money service provider integration

## Configuration Steps

### Step 1: Stripe Setup (Required for Card, Apple Pay, Google Pay)

1. **Create Stripe Account**
   - Go to https://stripe.com
   - Sign up for an account
   - Complete account verification

2. **Get API Keys**
   - Go to Stripe Dashboard → Developers → API Keys
   - Copy your Publishable Key and Secret Key

3. **Configure Environment Variables**
   ```bash
   # Add to your .env file or environment
   STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
   STRIPE_SECRET_KEY=sk_test_your_actual_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

4. **Set Up Webhooks**
   - Go to Stripe Dashboard → Developers → Webhooks
   - Add endpoint: `https://yourdomain.com/orders/webhook/stripe/`
   - Select events: `checkout.session.completed`, `payment_intent.payment_failed`
   - Copy the webhook secret to your environment variables

### Step 2: Apple Pay Setup (Optional)

1. **Domain Verification**
   - Go to Stripe Dashboard → Settings → Payment Methods → Apple Pay
   - Add your domain for verification
   - Download the verification file and place it in your static files

2. **Merchant ID** (if you have one)
   - Add your Apple Merchant ID to Stripe settings

### Step 3: Bank Transfer Setup

1. **Configure Bank Details**
   - Update bank account information in admin panel
   - Set up verification process for manual payments

2. **Admin Training**
   - Train admins to verify bank transfers
   - Set up email notifications for new transfers

### Step 4: USSD & Mobile Money Integration (Future)

For production use, you'll need to integrate with:
- **USSD**: Nigerian banks' USSD services
- **Mobile Money**: Paga, OPay, MTN Mobile Money, etc.

## Testing Payment Methods

### Test Cards (Stripe Test Mode)
```
Visa: 4242 4242 4242 4242
Mastercard: 5555 5555 5555 4444
American Express: 3782 822463 10005
```

### Test Scenarios
1. **Successful Payment**: Use any test card with valid future date
2. **Failed Payment**: Use 4000 0000 0000 0002
3. **Requires Authentication**: Use 4000 0025 0000 3155

## Security Considerations

1. **Never commit API keys to version control**
2. **Use environment variables for sensitive data**
3. **Enable HTTPS in production**
4. **Regular security audits**
5. **PCI compliance for card payments**

## Production Checklist

- [ ] Stripe API keys configured
- [ ] Webhook endpoint secured
- [ ] HTTPS enabled
- [ ] Error handling implemented
- [ ] Email notifications working
- [ ] Admin verification process in place
- [ ] Refund process tested
- [ ] Payment analytics working

## Troubleshooting

### Common Issues

1. **"Payment processing is not configured"**
   - Check if Stripe API keys are set correctly
   - Ensure keys are not the default placeholder values

2. **Webhook failures**
   - Verify webhook URL is accessible
   - Check webhook secret is correct
   - Ensure HTTPS is enabled

3. **Apple Pay/Google Pay not showing**
   - Verify domain is verified with Apple
   - Check if payment methods are enabled in Stripe

### Support

For payment-related issues:
- Check Stripe documentation: https://stripe.com/docs
- Review server logs for error messages
- Test with Stripe's test mode first

## Next Steps

1. **Complete Stripe setup** for card payments
2. **Test all payment flows** in development
3. **Set up production environment** with real API keys
4. **Integrate real USSD/Mobile Money** services as needed
5. **Monitor payment analytics** and optimize conversion rates 