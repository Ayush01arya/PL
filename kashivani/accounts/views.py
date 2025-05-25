from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import RegistrationForm, LoginForm, OTPVerificationForm
from .supabase_client import supabase_service
from .models import UserProfile
import base64


def register_view(request):
    """Registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if user already exists
            existing_user = supabase_service.get_user_by_email(form.cleaned_data['email'])
            if existing_user:
                messages.error(request, 'User with this email already exists.')
                return render(request, 'accounts/register.html', {'form': form})

            # Handle profile picture
            profile_pic_data = None
            if form.cleaned_data['profile_pic']:
                profile_pic = form.cleaned_data['profile_pic']
                profile_pic_data = base64.b64encode(profile_pic.read()).decode('utf-8')

            # Prepare user data for Supabase
            user_data = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'phone_number': form.cleaned_data['phone_number'],
                'description': form.cleaned_data['description'],
                'profile_pic': profile_pic_data,
                'is_verified': False
            }

            # Create user in Supabase
            created_user = supabase_service.create_user_profile(user_data)

            if created_user:
                # Generate and send verification email
                token = supabase_service.generate_verification_token()
                supabase_service.store_verification_token(form.cleaned_data['email'], token)

                if supabase_service.send_verification_email(
                        form.cleaned_data['email'],
                        token,
                        form.cleaned_data['name']
                ):
                    messages.success(request,
                                     'Registration successful! Please check your email to verify your account.')
                    return redirect('login')
                else:
                    messages.warning(request,
                                     'Registration successful, but we couldn\'t send the verification email. Please try to resend it.')
                    return redirect('login')
            else:
                messages.error(request, 'Registration failed. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login view - send OTP to email"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if user exists and is verified
            user = supabase_service.get_user_by_email(email)
            if not user:
                messages.error(request, 'No account found with this email address.')
                return render(request, 'accounts/login.html', {'form': form})

            if not user.get('is_verified', False):
                messages.error(request, 'Please verify your email address first.')
                return render(request, 'accounts/login.html', {'form': form})

            # Generate and send OTP
            otp = supabase_service.generate_otp()
            supabase_service.store_otp(email, otp)

            if supabase_service.send_otp_email(email, otp, user['name']):
                # Store email in session for OTP verification
                request.session['login_email'] = email
                messages.success(request, 'OTP sent to your email address.')
                return redirect('verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def verify_otp_view(request):
    """Verify OTP and complete login"""
    if 'login_email' not in request.session:
        messages.error(request, 'Please start the login process again.')
        return redirect('login')

    email = request.session['login_email']

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']

            if supabase_service.verify_otp(email, otp):
                # Get user data from Supabase
                user_data = supabase_service.get_user_by_email(email)

                # Create or get Django user
                django_user, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        'email': email,
                        'first_name': user_data['name']
                    }
                )

                # Create or update UserProfile
                user_profile, created = UserProfile.objects.get_or_create(
                    email=email,
                    defaults={
                        'user': django_user,
                        'name': user_data['name'],
                        'phone_number': user_data['phone_number'],
                        'description': user_data.get('description', ''),
                        'is_verified': user_data['is_verified']
                    }
                )

                # Log in the user
                login(request, django_user)

                # Clear the session
                del request.session['login_email']

                messages.success(request, f'Welcome back, {user_data["name"]}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'Please enter a valid 6-digit OTP.')
    else:
        form = OTPVerificationForm()

    return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})


def verify_email_view(request, token):
    """Verify email address using token"""
    # This is a simplified version - you'd want to get email from token
    # For now, we'll need to modify the token storage to include more info

    # You would typically decode the token to get the email
    # For this example, let's assume we can get it from the verification_tokens table
    try:
        # Get all verification tokens and find matching one
        # In a real app, you'd want a more secure way to do this
        result = supabase_service.supabase.table('verification_tokens').select("*").eq('token', token).execute()

        if result.data:
            email = result.data[0]['email']

            if supabase_service.verify_email_token(email, token):
                supabase_service.update_user_verification(email, True)
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Invalid or expired verification link.')
        else:
            messages.error(request, 'Invalid verification link.')
    except Exception as e:
        messages.error(request, 'Verification failed. Please try again.')

    return redirect('login')


@login_required
def dashboard_view(request):
    """Dashboard view for authenticated users"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Fallback if profile doesn't exist
        user_profile = None

    context = {
        'user': request.user,
        'user_profile': user_profile
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    """Logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')