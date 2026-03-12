"""
Custom JWT Authentication for Inventory System
Handles Bearer token authentication
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from datetime import datetime
from .models import User


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT Authentication class for API requests
    Extracts and validates JWT tokens from Authorization header
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token)
        Returns None if no authentication is attempted
        """
        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            # No token provided - allow unauthenticated access
            # (permissions will handle what they can access)
            return None
        
        try:
            # Extract token from "Bearer <token>" format
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                # If no "Bearer " prefix, assume entire header is token
                token = auth_header
            
            # Decode and verify token
            try:
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token has expired. Please login again.')
            except jwt.InvalidTokenError:
                raise AuthenticationFailed('Invalid token. Please login again.')
            
            # Extract user_id from payload
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')
            
            # Get user from database
            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found or inactive')
            
            # Return user and token
            return (user, token)
        
        except AuthenticationFailed:
            # Re-raise authentication failures
            raise
        except Exception as e:
            # Catch any other errors
            raise AuthenticationFailed(f'Authentication error: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return the authentication scheme to be used in the WWW-Authenticate header
        """
        return 'Bearer'