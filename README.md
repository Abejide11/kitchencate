# KitchenCrate - Nigerian Food Delivery E-commerce

A comprehensive Django-based e-commerce platform focused on Nigerian food delivery with integrated Nigerian payment systems.

## Features

### 🍽️ Core Features
- **Product Management**: Categories, products with images, pricing
- **Shopping Cart**: Session-based cart with quantity management
- **User Authentication**: Email-based registration and login
- **Order Management**: Complete order lifecycle tracking
- **Payment Integration**: Multiple Nigerian payment methods
- **Admin Dashboard**: Comprehensive admin interface
- **Mobile Responsive**: Modern, mobile-first design

### 💳 Payment Methods

#### 1. Credit/Debit Card (Stripe)
- **Supported Cards**: Visa, Mastercard, American Express
- **Currency**: Nigerian Naira (NGN)
- **Features**: Secure checkout, webhook handling, payment verification

#### 2. Bank Transfer
- **Process**: Direct bank transfer to KitchenCrate account
- **Features**: NUBAN support, transfer verification, receipt upload
- **Banks**: GT Bank, Zenith, Access, First Bank, UBA, and more

#### 3. Cash on Delivery
- **Process**: Pay when you receive your order
- **Features**: Automatic order confirmation, delivery tracking

#### 4. USSD Payment
- **Supported Banks**: GT Bank, Zenith, Access, First Bank, UBA, Fidelity, Ecobank, Stanbic, Union, Wema
- **Process**: Dial USSD code → Enter PIN → Confirm payment
- **Features**: Real-time code generation, bank-specific instructions

#### 5. Mobile Money
- **Providers**: Paga, OPay, Airtel Money, MTN MoMo, Vodafone Cash
- **Process**: Dial provider code → Enter phone → Confirm payment
- **Features**: Provider-specific codes, colorful UI, real-time validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-commerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate sample data**
   ```bash
   python manage.py populate_data
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (Credit/Debit Cards)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret


```

### Payment Gateway Setup

#### 1. Stripe Setup
1. Create account at [stripe.com](https://stripe.com)
2. Get API keys from Dashboard
3. Set up webhook endpoint: `https://yourdomain.com/orders/webhook/stripe/`
4. Add webhook events: `checkout.session.completed`



## 🧪 Testing Payment Methods

### Development Testing

1. **Skip Payment (Development)**
   - Use the "Skip Payment" button in checkout
   - Automatically marks orders as completed

2. **Stripe Test Cards**
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - Expiry: Any future date
   - CVC: Any 3 digits

3. **USSD Testing**
   - Use any 10-digit account number
   - Test with different bank codes

5. **Mobile Money Testing**
   - Use any phone number format
   - Test with different providers

### Production Testing

1. **Real Payment Processing**
   - Use real payment credentials
   - Test with small amounts
   - Verify webhook handling

2. **Bank Transfer Verification**
   - Upload real transfer receipts
   - Test admin verification process

## 📱 Mobile Money Providers

### Supported Providers

| Provider | Code | Color | Features |
|----------|------|-------|----------|
| Paga | *242*1*{phone}*{amount}# | Green | Mobile wallet, USSD |
| OPay | *955*{phone}*{amount}# | Orange | Digital banking, transfers |
| Airtel Money | *432*{phone}*{amount}# | Red | Mobile money, airtime |
| MTN MoMo | *165*{phone}*{amount}# | Yellow | Mobile money, transfers |
| Vodafone Cash | *110*{phone}*{amount}# | Red | Mobile money, payments |

### USSD Banking Codes

| Bank | USSD Code | Features |
|------|-----------|----------|
| GT Bank | *737*1*{account}*{amount}# | Quick banking, transfers |
| Zenith | *966*{account}*{amount}# | Mobile banking, payments |
| Access | *901*{account}*{amount}# | USSD banking, transfers |
| First Bank | *894*{account}*{amount}# | FirstMobile, payments |
| UBA | *919*{account}*{amount}# | UBA Mobile, transfers |
| Fidelity | *770*{account}*{amount}# | Fidelity Mobile, banking |
| Ecobank | *326*{account}*{amount}# | Ecobank Mobile, payments |
| Stanbic | *909*{account}*{amount}# | Stanbic Mobile, transfers |
| Union | *826*{account}*{amount}# | Union Mobile, banking |
| Wema | *945*{account}*{amount}# | Wema Mobile, payments |

## 🔧 Management Commands

### Payment Analytics
```bash
# Generate payment reports
python manage.py payment_analytics --format=json
python manage.py payment_analytics --format=csv
python manage.py payment_analytics --format=text
```

### Sample Data
```bash
# Create sample products and categories
python manage.py populate_data

# Generate product images
python manage.py generate_product_images

# Fix category slugs
python manage.py fix_category_slugs
```

## 📊 Admin Features

### Order Management
- **Order Tracking**: View all orders with status
- **Payment Verification**: Verify bank transfers and payments
- **Bulk Actions**: Process multiple orders
- **Analytics**: Payment statistics and reports

### Payment Features
- **Status Indicators**: Color-coded payment status
- **Method Icons**: Visual payment method identification
- **Verification Tools**: Bank transfer verification
- **Export Options**: Export payment data

## 🚀 Deployment

### Render.com Deployment
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Environment Variables for Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
PAYSTACK_SECRET_KEY=sk_live_your_key
FLUTTERWAVE_SECRET_KEY=sk_live_your_key
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected
- **Payment Verification**: Webhook signature verification
- **Input Validation**: Comprehensive form validation
- **Secure Headers**: Security middleware enabled
- **Environment Variables**: Sensitive data in .env

## 📞 Support

For payment-related issues:
1. Check webhook configurations
2. Verify API keys
3. Test with development credentials
4. Review payment logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test all payment methods
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**KitchenCrate** - Fresh meals delivered to your doorstep with secure Nigerian payment options. 