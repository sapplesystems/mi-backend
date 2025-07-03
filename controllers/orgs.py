import json
import graphene
from django.views import View
from django.http import JsonResponse
from graphql_jwt.decorators import login_required
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import views.orgs as orgs_view

from views.orgs import OrgType, register, get_org
from models.orgs.models import Orgs


# Create your views here.
class MapJsonView(View):
    def get(self, request):
        f = open('geojson/{}.json'.format(request.GET["name"]))
        # returns JSON object as
        # a dictionary
        data = json.load(f)
        return JsonResponse(data, status=200)


class Query(graphene.ObjectType):
    all_orgs = graphene.List(OrgType,
                             description='Return all orgs')

    @login_required
    def resolve_user(self, info):
        return info.context.user

    @login_required
    def resolve_all_orgs(self, info, **kwargs):
        return Orgs.objects.filter(**kwargs).order_by('name').all()


class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return register(request)


class OrgView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_org(request.user)


class UpdateOrgLogoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        return orgs_view.update_org_logo_url(request, org_id)


class GetAllOrgsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        return orgs_view.get_all_orgs(request)


class checkOrgPhoneNumber(APIView):

    def get(self, request):
        return orgs_view.check_for_valid_number(request)


class checkOrgName(APIView):

    def get(self, request):
        return orgs_view.check_for_valid_company_name(request)


class checkOrgAddress(APIView):

    def get(self, request):
        return orgs_view.check_for_valid_company_address(request)


class checkOrgGST(APIView):

    def get(self, request):
        return orgs_view.check_for_valid_gst_number(request)


class UpdateOrgView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, org_id):
        response = orgs_view.update_org(request, org_id)
        return response


class UpdateOrgStateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, org_id):
        response = orgs_view.update_org_state(request, org_id)
        return response


class OrgByIdView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, org_id):
        return orgs_view.get_org_by_id(org_id)
