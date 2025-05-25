import os
import secrets
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class SupabaseService:
    def __init__(self):
        # Initialize Supabase client
        # SUPABASE_URL = os.getenv('SUPABASE_URL')
        # SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        SUPABASE_URL = "https://rtkehbagrwajvhhvcuky.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0a2VoYmFncndhanZoaHZjdWt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMDQwNTUsImV4cCI6MjA2Mzc4MDA1NX0.UKC4_OmDlGnTGDmJLR52Gk5Gp9uf7XISfYKU152jZhQ"

        if not SUPABASE_URL or not SUPABASE_KEY:
            print(f"Missing environment variables:")
            print(f"SUPABASE_URL: {'✓' if SUPABASE_URL else '✗ Not set'}")
            print(f"SUPABASE_KEY: {'✓' if SUPABASE_KEY else '✗ Not set'}")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Supabase client: {e}")
            self.supabase = None
            raise

    def get_user_by_email(self, email):
        """Get user by email from Supabase"""
        try:
            if not self.supabase:
                raise RuntimeError("Supabase client not initialized")

            print(f"Checking if user exists with email: {email}")
            response = self.supabase.table('user_profiles').select("*").eq('email', email.lower().strip()).execute()

            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                print(f"User found: {response.data[0]}")
                return response.data[0]

            print("No user found with this email")
            return None

        except Exception as e:
            print(f"Error fetching user: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_user_profile(self, user_data):
        """Create user profile in Supabase"""
        try:
            if not self.supabase:
                raise RuntimeError("Supabase client not initialized")

            profile_data = {
                'name': str(user_data.get('name', '')).strip(),
                'email': str(user_data.get('email', '')).strip().lower(),
                'phone_number': str(user_data.get('phone_number', '')).strip() if user_data.get(
                    'phone_number') else None,
                'description': str(user_data.get('description', '')).strip() if user_data.get('description') else None,
                'profile_pic': user_data.get('profile_pic', None),
                'is_verified': bool(user_data.get('is_verified', False))
            }

            profile_data = {k: v for k, v in profile_data.items() if v is not None and v != ''}

            print(f"Attempting to create user profile with data: {profile_data}")

            response = self.supabase.table('user_profiles').insert(profile_data).execute()

            if hasattr(response, 'data') and response.data and len(response.data) > 0:
                print("User profile created successfully")
                return response.data[0]
            else:
                print(f"Failed to create user profile. Response: {response}")
                return None

        except Exception as e:
            print(f"Error creating user profile: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_verification_token(self):
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)

    def store_verification_token(self, email, token):
        """Store verification token in Supabase"""
        try:
            if not self.supabase:
                return False

            token_data = {
                'email': email,
                'token': token,
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }

            response = self.supabase.table('verification_tokens').insert(token_data).execute()
            return response.data is not None

        except Exception as e:
            print(f"Error storing verification token: {e}")
            return False

    def send_verification_email(self, email, token, name):
        """Send verification email using Django's email system"""
        try:
            verification_link = f"{settings.SITE_URL}/accounts/verify-email/{token}/"

            subject = 'Verify Your Email Address'

            # HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Email Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; text-align: center; padding: 20px; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Our Platform!</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {name}!</h2>
                        <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all;">{verification_link}</p>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you didn't create an account, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Your Company Name. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text version
            plain_message = f"""
            Hello {name}!

            Thank you for signing up! Please verify your email address by clicking the link below:

            {verification_link}

            This link will expire in 24 hours.

            If you didn't create an account, please ignore this email.

            © 2024 Your Company Name. All rights reserved.
            """

            # Send email using Django's email system
            from django.core.mail import EmailMultiAlternatives

            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            msg.attach_alternative(html_message, "text/html")

            result = msg.send()

            if result:
                print(f"✅ Verification email sent successfully to {email}")
                return True
            else:
                print(f"❌ Failed to send verification email to {email}")
                return False

        except Exception as e:
            print(f"Error sending verification email: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_otp(self):
        """Generate 6-digit OTP"""
        return f"{random.randint(100000, 999999)}"

    def store_otp(self, email, otp):
        """Store OTP in Supabase"""
        try:
            if not self.supabase:
                return False

            # Delete any existing OTPs for this email
            self.supabase.table('otp_codes').delete().eq('email', email).execute()

            otp_data = {
                'email': email,
                'otp': otp,
                'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
            }

            response = self.supabase.table('otp_codes').insert(otp_data).execute()
            return response.data is not None

        except Exception as e:
            print(f"Error storing OTP: {e}")
            return False

    def send_otp_email(self, email, otp, name):
        """Send OTP email using Django's email system"""
        try:
            subject = 'Your Login OTP Code'

            # HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>OTP Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2196F3; color: white; text-align: center; padding: 20px; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; text-align: center; background-color: #e3f2fd; padding: 20px; margin: 20px 0; border-radius: 8px; letter-spacing: 4px; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Login Verification</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {name}!</h2>
                        <p>You requested to login to your account. Please use the following OTP code:</p>
                        <div class="otp-code">{otp}</div>
                        <p>This code will expire in 10 minutes.</p>
                        <p>If you didn't request this code, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 Your Company Name. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Plain text version
            plain_message = f"""
            Hello {name}!

            You requested to login to your account. Please use the following OTP code:

            {otp}

            This code will expire in 10 minutes.

            If you didn't request this code, please ignore this email.

            © 2024 Your Company Name. All rights reserved.
            """

            # Send email using Django's email system
            from django.core.mail import EmailMultiAlternatives

            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            msg.attach_alternative(html_message, "text/html")

            result = msg.send()

            if result:
                print(f"✅ OTP email sent successfully to {email}")
                return True
            else:
                print(f"❌ Failed to send OTP email to {email}")
                return False

        except Exception as e:
            print(f"Error sending OTP email: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_otp(self, email, otp):
        """Verify OTP"""
        try:
            if not self.supabase:
                return False

            response = self.supabase.table('otp_codes').select("*").eq('email', email).eq('otp', otp).execute()

            if response.data and len(response.data) > 0:
                otp_record = response.data[0]
                expires_at = datetime.fromisoformat(otp_record['expires_at'].replace('Z', '+00:00'))

                if datetime.now() <= expires_at.replace(tzinfo=None):
                    # OTP is valid, delete it
                    self.supabase.table('otp_codes').delete().eq('id', otp_record['id']).execute()
                    return True
                else:
                    # OTP expired, delete it
                    self.supabase.table('otp_codes').delete().eq('id', otp_record['id']).execute()

            return False

        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return False

    def verify_email_token(self, email, token):
        """Verify email verification token"""
        try:
            if not self.supabase:
                return False

            response = self.supabase.table('verification_tokens').select("*").eq('email', email).eq('token',
                                                                                                    token).execute()

            if response.data and len(response.data) > 0:
                token_record = response.data[0]
                expires_at = datetime.fromisoformat(token_record['expires_at'].replace('Z', '+00:00'))

                if datetime.now() <= expires_at.replace(tzinfo=None):
                    # Token is valid, delete it
                    self.supabase.table('verification_tokens').delete().eq('id', token_record['id']).execute()
                    return True
                else:
                    # Token expired, delete it
                    self.supabase.table('verification_tokens').delete().eq('id', token_record['id']).execute()

            return False

        except Exception as e:
            print(f"Error verifying email token: {e}")
            return False

    def update_user_verification(self, email, is_verified):
        """Update user verification status"""
        try:
            if not self.supabase:
                return False

            response = self.supabase.table('user_profiles').update({'is_verified': is_verified}).eq('email',
                                                                                                    email).execute()
            return response.data is not None

        except Exception as e:
            print(f"Error updating user verification: {e}")
            return False


# Create service instance
try:
    supabase_service = SupabaseService()
except Exception as e:
    print(f"❌ Failed to initialize Supabase service: {e}")
    supabase_service = None