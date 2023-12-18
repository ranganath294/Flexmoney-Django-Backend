from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.http import JsonResponse
from rest_framework import status



def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        authentication = JWTAuthentication()
        try:
            authentication.authenticate(request)
            return view_func(request, *args, **kwargs)
        except AuthenticationFailed:
            return Response({'error': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)
    return wrapper


