from rest_framework.views import APIView

from views.contactus import contact_us


class ContactUsView(APIView):

    def post(self, request):
        return contact_us(request)
