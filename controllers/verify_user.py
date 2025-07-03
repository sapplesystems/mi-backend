from rest_framework.views import APIView
from views.verify_user import send_verification_code, check_verification_code, resend_verification_code


# view for send mail with verification and register verification code in db API
class SendVerificationCodeView(APIView):
    def post(self, request):
        response = send_verification_code(request)
        return response


class ReSendVerificationCodeView(APIView):
    def post(self, request):
        response = resend_verification_code(request)
        return response


# view for check verification code API
class CheckVerificationCodeView(APIView):
    def post(self, request):
        response = check_verification_code(request)
        return response
