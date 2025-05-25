from django import forms
from django.core.validators import RegexValidator


class RegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )

    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about yourself (optional)',
            'rows': 4
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You can add custom validation here if needed
        return email.lower()


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP',
            'maxlength': '6'
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        return otp