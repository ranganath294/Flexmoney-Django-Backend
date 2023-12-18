from django.urls import path
from . import views

urlpatterns = [
    # Sending Custom Emails
    path('custom_mail', views.custom_mail, name='custom_mail'),
    
    # Registations and Login
    path('register', views.register_user, name='register_user'),
    path('login', views.login_users, name='login_users'),
    path('logout', views.logout_users, name='logout_users'),
    path('verify_otp_registration',views.verify_otp_registration, name='verify_otp_registration'),

    # Fogot Password
    path('forgot_password_email_validation',views.forgot_password_email_validation, name='forgot_password_email_validation'),
    path('verify_otp_forgot_password',views.verify_otp_forgot_password, name='verify_otp_forgot_password'),
    path('change_password', views.change_password, name='change_password'),

    # Reset Password
    path('reset_password_email_validation', views.reset_password_email_validation, name='reset_password_email_validation'),
    path('verify_otp_reset_password',views.verify_otp_reset_password, name='verify_otp_reset_password'),
    path('reset_password', views.reset_password, name='reset_password'),
]

