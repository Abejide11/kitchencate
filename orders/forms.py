from django import forms
from .models import Order, BankTransferDetails


class OrderCreateForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[('card', 'Credit/Debit Card (Stripe)')],
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        initial='card',
        label='Payment Method'
    )
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'phone', 'payment_method']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BankTransferForm(forms.ModelForm):
    class Meta:
        model = BankTransferDetails
        fields = ['bank_name', 'account_name', 'account_number', 'nuban', 'routing_number', 'swift_code', 'iban', 'reference_number', 'transfer_date', 'transfer_amount', 'receipt_image', 'notes']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., GT Bank, Zenith Bank, Access Bank'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account number'}),
            'nuban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NUBAN (10-digit Nigerian account number)'}),
            'routing_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sort Code (UK) or Routing Number (US)'}),
            'swift_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SWIFT/BIC code (International)'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN (International)'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transfer reference number'}),
            'transfer_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transfer_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes about your transfer'}),
        }
        labels = {
            'bank_name': 'Bank Name',
            'account_name': 'Account Holder Name',
            'account_number': 'Account Number',
            'nuban': 'NUBAN',
            'routing_number': 'Sort Code/Routing Number',
            'swift_code': 'SWIFT/BIC Code',
            'iban': 'IBAN',
            'reference_number': 'Reference Number',
            'transfer_date': 'Transfer Date',
            'transfer_amount': 'Transfer Amount (₦)',
            'receipt_image': 'Upload Receipt',
            'notes': 'Additional Notes',
        } 