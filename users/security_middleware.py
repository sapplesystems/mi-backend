class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add headers to the response
        response['Access-Control-Allow-Methods'] = "GET, POST, OPTIONS"
        response[
            'Access-Control-Allow-Headers'] = "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range"
        response['Referrer-Policy'] = "same-origin"
        response['X-XSS-Protection'] = "1; mode=block"
        response['X-Frame-Options'] = "SAMEORIGIN"
        response['X-Content-Type-Options'] = "nosniff"
        response['X-Frame-Options'] = "DENY"
        response['Set-Cookie'] = "Path=/; HttpOnly; Secure"
        response['Strict-Transport-Security'] = "max - age = 31536000; includeSubDomains; preload;"
        response['Content-Security-Policy'] = "default-src 'self';"

        return response
