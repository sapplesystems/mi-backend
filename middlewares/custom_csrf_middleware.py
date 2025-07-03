# from django.middleware.csrf import get_token

from django.middleware.csrf import CsrfViewMiddleware

class CustomCSRFMiddleware(CsrfViewMiddleware):
    def process_response(self, request, response):
        # Set CSRF cookie for API requests
        if request.path.startswith('/api/'):
            self._set_token_cookie(request, response)

        return response

    def _set_token_cookie(self, request, response):
        csrf_token = self._get_token(request)
        response.set_cookie('csrftoken', csrf_token, secure=request.is_secure())

    def _get_token(self, request):
        if 'csrf_token' not in request.COOKIES:
            return self._get_new_token()
        return request.COOKIES['csrf_token']

    def _get_new_token(self):
        token = self._generate_token()
        self._save_token(token)
        return token

    def _generate_token(self):
        # Implement your own token generation logic here
        # You can use Django's get_random_string() method, for example
        from django.utils.crypto import get_random_string
        return get_random_string(32)

    def _save_token(self, token):
        # Implement your own token storage logic here if needed
        pass
# class CustomCSRFMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#
#         # Add CSRF token as a header for API responses
#         if request.path.startswith('/api/'):
#             response['X-CSRFToken'] = get_token(request)
#
#         return response