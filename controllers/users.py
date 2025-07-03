from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from views.users import add_user, user_login, check_user, get_all_users, update_user, register_user, \
    populate_user_roles, reset_password


# view for login API
class LoginView(APIView):

    def post(self, request):
        response = user_login(request)
        return response


# view for check user API
class CheckUserView(APIView):

    def get(self, request):
        response = check_user(request)
        return response


# view for set password API
class SetPasswordView(APIView):
    def post(self, request):
        tasks = add_user(request)
        return tasks


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        tasks = reset_password(request)
        return tasks


class GetUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        request_user = request.user
        user = {
            'id': request_user.id,
            'email': request_user.email,
            'is_superuser': request_user.is_superuser,
            'username': request_user.username,
            'first_name': request_user.first_name,
            'last_name': request_user.last_name,
            'is_staff': request_user.is_staff,
            'is_active': request_user.is_active,
            'date_joined': request_user.date_joined,
            'last_login': request_user.last_login,
            'role': request_user.user_role
        }
        return Response(user, status=status.HTTP_201_CREATED)


class CreateUserAPIToken(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        request_user = request.user
        token, created = Token.objects.get_or_create(user=request_user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class UpdateUserAPIToken(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        request_user = request.user
        token = Token.objects.get(user=request_user)
        if token:
            token.delete()
        token, created = Token.objects.get_or_create(user=request_user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class GetUserAPIToken(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        request_user = request.user
        try:
            token = Token.objects.get(user=request_user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "No API token found."}, status=status.HTTP_404_NOT_FOUND)


class RefreshTokenView(TokenRefreshView):
    pass


class RegisterUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        response = register_user(request)
        return response


class GetAllUsersView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    pagination_class = PageNumberPagination

    def get(self, request):
        response = get_all_users(request)
        return response


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, user_id):
        response = update_user(request, user_id)
        return response


class PopulateUserRolesView(APIView):
    # permission_classes = [IsAuthenticated]
    # parser_classes = [JSONParser]

    def post(self, request):
        response = populate_user_roles(request)
        return response
