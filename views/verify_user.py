import logging
import os

from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
from validate_email_address import validate_email
from datetime import datetime, timedelta
from django.utils import timezone
from models.verify_user.models import verify_user
from models.verify_user.schema import get_user_verification_code, decrease_user_verification_code_check_count, \
    check_mail_sent_to_user, check_mail_resent_to_user
from settings.base import BASE_DIR
from views.utils import genarate_verification_code, format_and_send_mail


def register_code(email, code):
    expiry_date = datetime.now() + timedelta(hours=24)
    data = {'verification_code': code,
            'expiry': expiry_date,
            'count': 5,
            'resend_flag': True}
    obj_store, created = verify_user.objects.update_or_create(email=email, defaults=data)


def send_verification_code(request):
    email = request.data['email']
    now = timezone.now()
    code_db = check_mail_sent_to_user(email, now)
    if code_db:
        return Response({"msg": "Email has already been sent."}, status=status.HTTP_409_CONFLICT)
    else:
        isValidEmail = validate_email(email)
        if isValidEmail:
            code = genarate_verification_code()
            register_code(email, code)

            # form email parameters to send mail with verification code to user
            context = {'code': code}
            template = "send_otp.html"
            to_email = [email]
            subject = 'Made in India Label | One-Time Password'

            # format email template & send mail with verification code to user
            format_and_send_mail(template, subject, context, to_email)

            return Response({'msg': "Email has been sent."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Email not valid."}, status=status.HTTP_400_BAD_REQUEST)


def check_verification_code(request):
    email = request.data['email']
    code = request.data['code']
    now = timezone.now()
    code_db = get_user_verification_code(email, code, now)
    if code_db:
        return Response({'msg': 'Code verified successfully.'}, status=status.HTTP_200_OK)
    else:
        count = decrease_user_verification_code_check_count(email, now)
        if count >= 0:
            return Response({'error': 'Incorrect verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Max retries exceeded.'}, status=status.HTTP_400_BAD_REQUEST)


def re_register_code(email, code):
    expiry_date = datetime.now() + timedelta(hours=24)
    data = {'verification_code': code,
            'expiry': expiry_date,
            'count': 5,
            'resend_flag': False}
    obj_store, created = verify_user.objects.update_or_create(email=email, defaults=data)


def resend_verification_code(request):
    email = request.data['email']
    code_db = check_mail_resent_to_user(email)
    if code_db:
        return Response({"msg": "Email has already been sent."}, status=status.HTTP_409_CONFLICT)
    else:
        isValidEmail = validate_email(email)
        if isValidEmail:
            code = genarate_verification_code()
            re_register_code(email, code)

            # form email parameters to send mail with verification code to user
            context = {'code': code}
            template = "send_otp.html"
            to_email = [email]
            subject = 'Made in India Label | One-Time Password'

            # format email template & send mail with verification code to user
            format_and_send_mail(template, subject, context, to_email)

            return Response({'msg': "Email has been sent."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Email not valid."}, status=status.HTTP_400_BAD_REQUEST)
