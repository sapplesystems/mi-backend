import secrets
import string
from random import choice
from django.core.mail import EmailMessage
import logging
from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
import os
import boto3
from botocore.exceptions import ClientError
from users.models import User
from users.schema import get_user

s3 = boto3.client('s3')


# generate random 4 digit code
def genarate_verification_code():
    chars = string.digits
    random = ''.join(choice(chars) for _ in range(4))
    return random


# send mail
def send_email(data, from_email=os.getenv("FROM_EMAIL", "noreply@emailer.qci.solutions")):
    # create cc_list for email
    cc_list = []
    if data['cc_mail']:
        cc_list.extend(data['cc_mail'])

    # create bcc_list for email
    bcc_list = ["mayur@dataorc.in", "navdeep@dataorc.in", "abhilash@dataorc.in"]

    try:
        environment = os.getenv("ENV", "")
        if environment != "":
            environment = "[Staging] "
        email = EmailMessage(
            subject=str(environment) + data['subject'],
            body=data['html_message'],
            from_email=from_email,
            to=data['to_email'],
            cc=cc_list,
            bcc=bcc_list,
        )
        email.content_subtype = "html"
        email.send()
        return True
    except Exception:
        logging.exception(Exception)
        return False


def create_presigned_url(bucket_name, object_name, expiration=604800):
    try:
        response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=expiration)
    except ClientError as e:
        return {"error": f"Couldn't get signed url - {e}"}
    return response


def add_user(email, role):
    email = email
    role = role
    letters = string.ascii_letters
    digits = string.digits
    alphabet = letters + digits
    pwd_length = 12
    password = ''
    for i in range(pwd_length):
        password += ''.join(secrets.choice(alphabet))
    username = get_user(email)
    if username:
        return Response({"msg": "User is already exists."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            user = User.objects.create_user(email=email, username=email, user_role=role)
            user.set_password(password)
            user.save()

            # form email parameters to send mail to supervisor
            context = {'user': email, 'role': role, 'pwd': password}
            template = "register_user.html"
            to_email = [email]
            subject = 'Made in India Label | User Registered'

            # format email template & send mail to supervisor
            format_and_send_mail(template, subject, context, to_email)
            return user
        except:
            return None


def format_and_send_mail(template, subject, context, to_mail, cc_mail=None):
    template = get_template(template).render(context)
    data = {
        'subject': subject,
        'body': context,
        'to_email': to_mail,
        'html_message': template,
        'cc_mail': cc_mail
    }
    response = send_email(data)
