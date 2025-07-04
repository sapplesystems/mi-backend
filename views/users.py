import os
import secrets
import string

import requests
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from models.applications.models import ApplicationSupervisor
from models.orgs.schema import get_org_by_user
from users.models import User
from users.schema import get_user
from users.serializer import UserListSerializer
from users.utils import get_tokens_for_user
from utils.func import is_valid_email, validate_captcha
from views.utils import format_and_send_mail
from users import schema as user_schema

from django.contrib.auth.hashers import check_password


def check_user(request):
    token = request.query_params['token']
    result_json = validate_captcha(token)
    if not result_json.get('success'):
        return Response({'error': 'Invalid captcha.'}, status=status.HTTP_403_FORBIDDEN)
    else:
        email = request.query_params['email']
        user = get_user(email)
        if user:
            return Response({'msg': 'User exists.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Please enter valid details'}, status=status.HTTP_400_BAD_REQUEST)


def add_user(request):
    email = request.data['email']
    password1 = request.data['password1']
    password2 = request.data['password2']
    if password1 == password2:
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(password1)
            user.save()
        else:
            user = User.objects.create_user(email=email, username=email, user_role="org_admin")
            user.set_password(password1)
            user.save()
        return Response({"msg": "User created."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Password mismatch."}, status=status.HTTP_400_BAD_REQUEST)


def reset_password(request):
    token = request.data.get('token')
    result_json = validate_captcha(token)
    if not result_json.get('success'):
        return Response({'error': 'Invalid captcha.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        email = request.data['email']
        old_password = request.data['old_password']
        password1 = request.data['password1']
        password2 = request.data['password2']
        if check_password(old_password, request.user.password):
            if password1 == password2:
                user = User.objects.filter(email=email).first()
                if user:
                    user.set_password(password1)
                    user.save()
                    return Response({"msg": "Password has been reset."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Password mismatch."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Existing password incorrect."}, status=status.HTTP_400_BAD_REQUEST)


def user_login(request):
    #result_json = validate_captcha(request.data.get('token'))
    #if not result_json.get('success'):
    #    return Response({'error': 'Invalid captcha.'}, status=status.HTTP_400_BAD_REQUEST)
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise AuthenticationFailed(
            'username and password required')

    user = User.objects.filter(username=username).first()
    if user is None:
        raise AuthenticationFailed('Please enter valid details.')
    if not user.check_password(password):
        raise AuthenticationFailed('Please enter valid details.')

    if user.user_role in ["org_admin", "applicant"]:
        org = get_org_by_user(user.id)
        if org and org.enabled is False:
            return Response({"error": "You are not authorized user."}, status=status.HTTP_400_BAD_REQUEST)

    token = get_tokens_for_user(user)
    access_token = token['access']
    refresh_token = token['refresh']

    response.set_cookie(key='refresh_token', value=refresh_token, httponly=False)
    response.set_cookie(key='access_token', value=access_token, httponly=True)

    response.data = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    return response


def register_user(request):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        email = request.data['email']
        role = request.data['role']
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

                return Response({"msg": "User created."}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": "Error in user creation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_all_users(request):
    if request.user.user_role not in ['super_admin', 'admin']:
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        excluded_values = ["super_admin", "applicant", "branch_user", "org_admin"]
        query = request.query_params.get("query", "")
        role = request.query_params.get("role", "")
        page_number = request.query_params.get("page", 1)
        items_per_page = 10
        filters = Q(Q(email__icontains=query) & Q(user_role__icontains=role))
        queryset = User.objects.filter(filters).exclude(user_role__in=excluded_values).order_by('-date_joined')
        if len(queryset) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if queryset:
                total_count = queryset.count()
                paginator = Paginator(queryset, items_per_page)
                try:
                    page = paginator.page(page_number)
                except EmptyPage:
                    return Response({'message': 'No more pages available'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = UserListSerializer(page, many=True)
                for data in serializer.data:
                    if data['user_role'] == "supervisor":
                        application_count = ApplicationSupervisor.objects.filter(reviewer_id=data['id']).count()
                        data['assigned_application_count'] = application_count
                result_data = {'users': serializer.data, 'total_count': total_count}
                return Response(result_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': "Users does not exists"}, status=status.HTTP_400_BAD_REQUEST)


def update_user(request, user_id):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = request.data
        user = user_schema.update_user(data, user_id)
        return Response({"msg": "Role has been updated."}, status=status.HTTP_200_OK)


def populate_user_roles(request):
    User.objects.filter(is_staff=True).update(user_role="admin")
    User.objects.filter(is_staff=False).update(user_role="applicant")
    return Response("User roles has been populated.", status=status.HTTP_200_OK)
