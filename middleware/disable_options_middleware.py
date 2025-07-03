from django.http import HttpResponseNotAllowed, HttpResponse


class DisableOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ['OPTIONS', 'DELETE', 'HEAD']:
            response = HttpResponse(status=405)  # Method Not Allowed
        else:
            response = self.get_response(request)
        return response
