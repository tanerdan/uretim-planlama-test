import base64
from django.http import HttpResponse
from django.conf import settings
import os

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sadece production ortamında basic auth uygula
        if not getattr(settings, 'BASIC_AUTH_ENABLED', False):
            return self.get_response(request)
        
        # Admin ve API endpointleri için basic auth kontrolü
        if request.path.startswith('/admin/') or request.path.startswith('/api/'):
            if not self.is_authenticated(request):
                return self.authentication_required()
        
        return self.get_response(request)

    def is_authenticated(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return False
        
        try:
            auth_type, auth_string = auth_header.split(' ', 1)
            if auth_type.lower() != 'basic':
                return False
            
            auth_string = base64.b64decode(auth_string).decode('utf-8')
            username, password = auth_string.split(':', 1)
            
            # Environment variables'dan kullanıcı bilgilerini al
            expected_username = os.environ.get('BASIC_AUTH_USERNAME', 'testuser')
            expected_password = os.environ.get('BASIC_AUTH_PASSWORD', 'testpass123')
            
            return username == expected_username and password == expected_password
        except:
            return False

    def authentication_required(self):
        response = HttpResponse('Authentication required', status=401)
        response['WWW-Authenticate'] = 'Basic realm="Test Environment"'
        return response