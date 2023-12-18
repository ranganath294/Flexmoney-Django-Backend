import random
from django.core.mail import send_mail
from django.conf import settings


# error emails from server


def send_otp_via_email_for_registration(email): 
    otp = random.randint(100000, 999999)
    subject = "Verify Your Email"
    message = f'Your otp is {otp}. OTP will be expired in 10 minutes'
    email_from = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, email_from, [email], fail_silently=False)
    

    return otp



def send_otp_via_email_for_forgot_password(email): 
    otp = random.randint(100000, 999999)
    subject = "OTP For Verifying Email - Forgot Password"
    message = f'Your otp is {otp}. OTP will be expired in 10 minutes'
    email_from = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, email_from, [email], fail_silently=False)
    

    return otp



def send_otp_via_email_for_reset_password(email): 
    otp = random.randint(100000, 999999)
    subject = "OTP For Verifying Email - Reset Password"
    message = f'Your otp is {otp}. OTP will be expired in 10 minutes'
    email_from = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, email_from, [email], fail_silently=False)
    

    return otp



def send_custom_mail(email,msg): 
    subject = "Custom"
    message = msg
    email_from = settings.EMAIL_HOST_USER
    
    send_mail(subject, message, email_from, [email], fail_silently=False)
    
