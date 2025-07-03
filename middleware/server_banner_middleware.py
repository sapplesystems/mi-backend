class ServerBannerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Server'] = 'My Custom Server'  # Replace 'My Custom Server' with your desired server banner
        return response
