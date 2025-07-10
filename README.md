# KitchenCrate - Food Ordering Website with Django

A modern, full-featured food ordering website built with Django and Python. KitchenCrate lets customers browse delicious meals, add them to their cart, and order for delivery or pickup. Features include user authentication, menu management, order processing, and Stripe payment integration.

## Features

### 🍽️ **Food Ordering Experience**
- **Menu Catalog**: Browse meals by categories (Rice, Seafood, Swallow, Soup, Pasta, Assorted Meat/Snack) with search and filtering
- **Meal Details**: Comprehensive meal information with images and descriptions
- **Cart**: Add, remove, and update food items with real-time calculations
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5

### 👤 **User Management**
- **User Registration & Login**: Secure authentication with email verification
- **User Dashboard**: Personal dashboard with order history and account information
- **Profile Management**: View and manage account details

### 💳 **Payment & Orders**
- **Stripe Integration**: Secure payment processing with Stripe
- **Order Management**: Complete order lifecycle from creation to delivery
- **Order Tracking**: Real-time order status updates
- **Order History**: View all past orders with detailed information

### 🛠️ **Admin Features**
- **Product Management**: Add, edit, and manage products and categories
- **Order Management**: Process orders and update status
- **Inventory Management**: Track stock levels and availability
- **User Management**: Manage customer accounts

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (can be easily changed to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Payment**: Stripe API
- **Authentication**: Django Allauth
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Images**: Pillow for image processing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd e-commerce
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
```

### Step 5: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 8: Run the Development Server
```bash
python manage.py runserver
```

The website will be available at `http://127.0.0.1:8000/`

## Project Structure

```
e-commerce/
├── ecommerce/                 # Main Django project
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── store/                    # Store app (products, categories)
│   ├── models.py             # Product and Category models
│   ├── views.py              # Product views
│   ├── urls.py               # Store URLs
│   └── admin.py              # Admin configuration
├── cart/                     # Shopping cart functionality
│   ├── cart.py               # Cart class
│   ├── views.py              # Cart views
│   └── context_processors.py # Cart context processor
├── orders/                   # Order management
│   ├── models.py             # Order models
│   ├── views.py              # Order views
│   ├── forms.py              # Order forms
│   └── admin.py              # Order admin
├── accounts/                 # User account management
│   ├── views.py              # Account views
│   └── urls.py               # Account URLs
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   ├── store/                # Store templates
│   ├── cart/                 # Cart templates
│   ├── orders/               # Order templates
│   └── accounts/             # Account templates
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User-uploaded files
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
└── README.md                 # This file
```

## Usage

### For Customers
1. **Browse Menu**: Visit the homepage to see all available meals
2. **Add to Cart**: Click "Add to Cart" on any meal
3. **Manage Cart**: View cart, update quantities, or remove items
4. **Checkout**: Proceed to checkout and enter delivery or pickup information
5. **Payment**: Complete payment using Stripe
6. **Track Orders**: View order status and history in your dashboard

### For Administrators
1. **Access Admin Panel**: Go to `/admin/` and login with superuser credentials
2. **Manage Products**: Add, edit, or remove products and categories
3. **Process Orders**: Update order status and manage inventory
4. **User Management**: View and manage customer accounts

## Stripe Configuration

### Test Cards for Development
- **Visa**: 4242 4242 4242 4242
- **Mastercard**: 5555 5555 5555 4444
- **American Express**: 3782 822463 10005

### Webhook Setup
1. Install Stripe CLI
2. Run: `stripe listen --forward-to localhost:8000/orders/webhook/`
3. Copy the webhook signing secret to your `.env` file

## Customization

### Adding New Features
- **Product Reviews**: Add review models and views
- **Wishlist**: Implement wishlist functionality
- **Email Notifications**: Add email templates for order confirmations
- **Discount Codes**: Implement coupon system
- **Multiple Payment Methods**: Add PayPal, Apple Pay, etc.

### Styling
- Modify `templates/base.html` for global styling changes
- Update Bootstrap classes in templates
- Add custom CSS in the `<style>` section or create separate CSS files

## Deployment

### Production Settings
1. Set `DEBUG=False` in settings
2. Configure production database (PostgreSQL recommended)
3. Set up proper static file serving
4. Configure email backend
5. Set up SSL/HTTPS
6. Configure Stripe webhooks for production

### Recommended Hosting
- **Heroku**: Easy deployment with PostgreSQL add-on
- **DigitalOcean**: VPS with Django deployment
- **AWS**: EC2 with RDS database
- **PythonAnywhere**: Django-friendly hosting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the Django documentation
- Review Stripe documentation for payment-related issues

## Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- Stripe for payment processing
- Font Awesome for icons 