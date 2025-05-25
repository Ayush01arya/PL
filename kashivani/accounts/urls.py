from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.login_view, name='home'),  # Redirect root to login
]