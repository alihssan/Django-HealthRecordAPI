from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        jwt_authenticator = JWTAuthentication()
        try:
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is not None:
                request.user, _ = user_auth_tuple
        except Exception:
            pass 