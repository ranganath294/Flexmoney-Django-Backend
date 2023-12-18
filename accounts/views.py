from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import MyUser, Email_verification
from .emails import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from .decorators import *



def validate_password(string):
    has_number = any(char.isdigit() for char in string)
    has_uppercase = any(char.isupper() for char in string)
    has_lowercase = any(char.islower() for char in string)
    has_special_char = not string.isalnum()

    return has_number, has_uppercase, has_lowercase, has_special_char



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



# Registration

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email")
            name = request.data.get("name")
            dob = request.data.get("dob")
            mobile = request.data.get("mobile")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not name:
                return Response({"msg": "No name sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not dob:
                return Response({"msg": "No dob sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not mobile:
                return Response({"msg": "No mobile sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({"msg": "No password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not confirm_password:
                return Response({"msg": "No confirm_password sent"}, status=status.HTTP_400_BAD_REQUEST)

            # no mobile validation 

            email_exists = MyUser.objects.filter(email=email)
            if email_exists.exists():
                if email_exists.first().is_verified:
                    return Response({"msg": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"msg": "Email Registered. Verification Pending"}, status=status.HTTP_400_BAD_REQUEST)

            if(password != confirm_password):
                return Response({"msg": "Password does not match"}, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 9:
                return Response({"msg": "Password very small"}, status=status.HTTP_400_BAD_REQUEST)
            
            number, uppercase, lowercase, special_char = validate_password(password)

            if not number:
                return Response({"msg": "Password does not have atleast one number"}, status=status.HTTP_400_BAD_REQUEST)
            if not uppercase:
                return Response({"msg": "Password does not have atleast one Uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
            if not lowercase:
                return Response({"msg": "Password does not have atleast one Lowercase letter"}, status=status.HTTP_400_BAD_REQUEST)
            if not special_char:
                return Response({"msg": "Password does not have atleast one special characters"}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = send_otp_via_email_for_registration(email)

            # creating an user instance
            user = MyUser.objects.create_user(email=email, password=password, dob=dob, name=name, mobile=mobile)
            user.save()
            
            # storing otp with email (for referencing otp) temporarily
            email_verification = Email_verification.objects.create(email=email, otp=otp)
            email_verification.save()

            # not verified otp. So is_verified will be false.

            return Response({"msg": "Registration Successful. Verify Email"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)




# Login 

@api_view(['POST'])
def login_users(request):
    try:
        if request.method == 'POST':
            email = request.data.get("email", None)
            password = request.data.get("password", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({"msg": "No password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            email_exists = MyUser.objects.filter(email=email).exists()
            
            if not (email_exists):
                return Response({"msg": "Email not registered"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = authenticate(email=email, password=password)
                if user is None:
                    return Response({"msg": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    token = get_tokens_for_user(user=user)
                    return Response({"msg": "Login Successful", "access_token": token["access"], "refresh_token": token["refresh"]}, status=status.HTTP_200_OK)
                    

    except Exception as e:
        # print(e)
        return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Logging out 
@api_view(['POST'])
def logout_users(request):
    if request.method == 'POST':
        try:
            # logout(request)
            refresh_token = request.data.get("refresh_token", None)
            
            if not refresh_token:
                return Response({"msg": "No refresh_token sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Verifing OTP For registration 

@api_view(['POST'])
def verify_otp_registration(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            otp = request.data.get("otp", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not otp:
                return Response({"msg": "No otp sent"}, status=status.HTTP_400_BAD_REQUEST)

            email_verification  = Email_verification.objects.get(email=email)
            
            if email_verification.otp_is_valid():
                pass
            else:
                email_verification.delete()
                return Response({"msg": "OTP Expired"}, status=status.HTTP_400_BAD_REQUEST)
                
            otp_sent = email_verification.otp

            user = MyUser.objects.get(email=email)

            if otp != otp_sent:
                return Response({"msg": "OTP wrong"}, status=status.HTTP_400_BAD_REQUEST)
            elif email !=user.email:
                return Response({"msg": "Email not matched"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.is_verified = True
                user.is_active = True
                user.save()

                email_verification.delete()

                token = get_tokens_for_user(user=user)

                return Response({"msg": "Registration Successful", "access_token": token["access"], "refresh_token": token["refresh"]}, status=status.HTTP_200_OK)

        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Sending OTP in email for forgot password 

@api_view(['POST'])
def forgot_password_email_validation(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            if email:
                email_exists = MyUser.objects.filter(email=email).exists()
                if not (email_exists):
                    return Response({"msg": "Email not registered"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    otp = send_otp_via_email_for_forgot_password(email)
                    
                    # storing otp with email (for referencing otp) temporarily
                    email_verification = Email_verification.objects.create(email=email, otp=otp)
                    email_verification.save()
                    return Response({"msg": "OTP sent to Registered email"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "No Email sent"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Verifing OTP For Forgot Password

@api_view(['POST'])
def verify_otp_forgot_password(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            otp = request.data.get("otp", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not otp:
                return Response({"msg": "No otp sent"}, status=status.HTTP_400_BAD_REQUEST)

            email_verification  = Email_verification.objects.get(email=email)
            
            if email_verification.otp_is_valid():
                pass
            else:
                email_verification.delete()
                return Response({"msg": "OTP Expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            otp_sent = email_verification.otp

            user = MyUser.objects.get(email=email)

            if otp != otp_sent:
                return Response({"msg": "otp wrong"}, status=status.HTTP_400_BAD_REQUEST)
            elif email !=user.email:
                return Response({"msg": "email not matched"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                email_verification.delete()

                return Response({"msg": "Email Validated"}, status=status.HTTP_200_OK)

        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)




# Changing Password For Forgot password 

@api_view(['POST'])
def change_password(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            password = request.data.get("password", None)
            confirm_password = request.data.get("confirm_password", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({"msg": "No password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not confirm_password:
                return Response({"msg": "No confirm_password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if email and password and confirm_password:
                user = MyUser.objects.filter(email=email)
                email_exists = user.exists()
                user = user.first()

                number, uppercase, lowercase, special_char = validate_password(password)

                if not (email_exists):
                    return Response({"msg": "Email not registered"}, status=status.HTTP_400_BAD_REQUEST)
                elif password != confirm_password:
                    return Response({"msg": "Password and Confirm Password are not same"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(password) < 9:
                    return Response({"msg": "Password very small"}, status=status.HTTP_400_BAD_REQUEST)
                elif not number:
                    return Response({"msg": "Password does not have atleast one number"}, status=status.HTTP_400_BAD_REQUEST)
                elif not uppercase:
                    return Response({"msg": "Password does not have atleast one Uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
                elif not lowercase:
                    return Response({"msg": "Password does not have atleast one Lowercase letter"}, status=status.HTTP_400_BAD_REQUEST)
                elif not special_char:
                    return Response({"msg": "Password does not have atleast one special characters"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(password)
                    user.save()
                    return Response({"msg": "Password Changed Successfully"}, status=status.HTTP_200_OK)
                
        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Sending OTP in email for reset password 

@api_view(['POST'])
@login_required
def reset_password_email_validation(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            if email:
                email_exists = MyUser.objects.filter(email=email).exists()
                if not (email_exists):
                    return Response({"msg": "Email not registered"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    otp = send_otp_via_email_for_reset_password(email)
                    
                    # storing otp with email (for referencing otp) temporarily
                    email_verification = Email_verification.objects.create(email=email, otp=otp)
                    email_verification.save()
                    return Response({"msg": "OTP sent to Registered email"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "No Email sent"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



# Verifing OTP 

@api_view(['POST'])
@login_required
def verify_otp_reset_password(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            otp = request.data.get("otp", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not otp:
                return Response({"msg": "No otp sent"}, status=status.HTTP_400_BAD_REQUEST)

            email_verification  = Email_verification.objects.get(email=email)
            
            if email_verification.otp_is_valid():
                pass
            else:
                email_verification.delete()
                return Response({"msg": "OTP Expired"}, status=status.HTTP_400_BAD_REQUEST)
            
            otp_sent = email_verification.otp

            user = MyUser.objects.get(email=email)

            if otp != otp_sent:
                return Response({"msg": "otp wrong"}, status=status.HTTP_400_BAD_REQUEST)
            elif email !=user.email:
                return Response({"msg": "email not matched"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                email_verification.delete()

                return Response({"msg": "Email Validated"}, status=status.HTTP_200_OK)

        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)




# Resetting Password 

@api_view(['POST'])
@login_required
def reset_password(request):
    if request.method == 'POST':
        try:
            email = request.data.get("email", None)
            password = request.data.get("password", None)
            confirm_password = request.data.get("confirm_password", None)

            if not email:
                return Response({"msg": "No email sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({"msg": "No password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not confirm_password:
                return Response({"msg": "No confirm_password sent"}, status=status.HTTP_400_BAD_REQUEST)
            
            if email and password and confirm_password:
                user = MyUser.objects.filter(email=email)
                email_exists = user.exists()
                user = user.first()

                number, uppercase, lowercase, special_char = validate_password(password)

                if not (email_exists):
                    return Response({"msg": "Email not registered"}, status=status.HTTP_400_BAD_REQUEST)
                elif password != confirm_password:
                    return Response({"msg": "Password and Confirm Password are not same"}, status=status.HTTP_400_BAD_REQUEST)
                elif len(password) < 9:
                    return Response({"msg": "Password very small"}, status=status.HTTP_400_BAD_REQUEST)
                elif not number:
                    return Response({"msg": "Password does not have atleast one number"}, status=status.HTTP_400_BAD_REQUEST)
                elif not uppercase:
                    return Response({"msg": "Password does not have atleast one Uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
                elif not lowercase:
                    return Response({"msg": "Password does not have atleast one Lowercase letter"}, status=status.HTTP_400_BAD_REQUEST)
                elif not special_char:
                    return Response({"msg": "Password does not have atleast one special characters"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(password)
                    user.save()
                    return Response({"msg": "Password Changed Successfully"}, status=status.HTTP_200_OK)
                
        except Exception as e:
            # print(e)
            return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@login_required
def custom_mail(request):
    if request.method == 'POST':
        data=request.data
        send_custom_mail(data["email"],data["msg"])
        
        return Response({"msg": "Email Sent"}, status=status.HTTP_200_OK)