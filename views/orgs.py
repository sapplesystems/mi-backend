import logging
import datetime
import os

from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
from graphene_django.types import DjangoObjectType

from models.orgs.models import Orgs
import models.orgs.schema as org_schema
from models.orgs.serializer import OrgSerializer, OrgBranchSerializer, OrgPartnerSerializer
from models.orgs.schema import register_org, register_org_partners, register_org_branches
from users.schema import get_user_email, get_user
from utils.func import is_valid_phone_number
from views.utils import add_user, format_and_send_mail


class OrgType(DjangoObjectType):
    class Meta:
        model = Orgs


def register(request):
    org_data = {'user': request.user.id, 'company_address': request.data.get('company_address'),
                'registered_company_name': request.data.get('registered_company_name'),
                'gst_number': request.data.get('gst_number'),
                'company_email': request.data.get('email'), 'mobile_number': request.data.get('mobile_number'),
                'aadhar_no': request.data.get('aadhar_number', None), 'pan_no': request.data.get('pan_no', None),
                'tan_no': request.data.get('tan_no', None), 'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now(), 'logo_url': request.data.get('logo_url', None),
                'company_website': request.data.get('company_website', None), }
    # add entry for org and return org id
    try:
        org_id = register_org(org_data)['id']
        # form email parameters to send mail to applicant regarding org registration
        context = {'org': org_data['registered_company_name']}
        template = "register_org.html"
        to_email = [request.user.email]
        subject = 'Made in India Label | Registration Confirmation'

        # format email template & send mail to applicant regarding org registration
        format_and_send_mail(template, subject, context, to_email)

        return Response({"msg": 'Organization has been registered.', "org_id": org_id}, status=status.HTTP_200_OK)
    except Exception as error:
        logging.exception(error)
        return Response(error.args[0], status=status.HTTP_400_BAD_REQUEST)


def get_org(user):
    if user.user_role in ["org_admin", "applicant"]:
        org = org_schema.get_org_by_user(user.id)
    elif user.user_role == "branch_user":
        org = org_schema.get_org_by_branch_user(user.id).org
    org_data = {}
    if org:
        org_data['org'] = OrgSerializer(org).data
        s3_url = os.getenv("S3_URL")  # TODO: ADD this in infra ENV
        company_logo = org_data['org']['logo_url']
        if company_logo and s3_url:
            company_logo = s3_url + company_logo
        org_data['org']['logo_url'] = company_logo
        branch = org_schema.get_branch_by_org_id(org.id)
        if branch:
            org_branch = OrgBranchSerializer(branch, many=True)
            org_branches = org_branch.data
            for orgbranch in org_branches:
                orgbranch['email'] = get_user_email(orgbranch['user'])['username']
            org_data['org_branches'] = org_branches
        partner = org_schema.get_partner_by_org_id(org.id)
        if partner:
            org_partner = OrgPartnerSerializer(partner, many=True)
            org_data['org_partners'] = org_partner.data
        return Response(org_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Org does not exists"}, status=status.HTTP_400_BAD_REQUEST)


def update_org_logo_url(request, org_id):
    logo_url = request.data.get('logo_url')
    org = org_schema.update_org_logo_url_schema(org_id, logo_url)
    if org:
        return Response({"msg": "Logo Url Updated."}, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Org does not exists"}, status=status.HTTP_400_BAD_REQUEST)


def get_all_orgs(request):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        query = request.query_params.get("query", "")
        page_number = request.query_params.get("page", 1)
        items_per_page = 10
        filters = Q(company_email__icontains=query) | Q(registered_company_name__icontains=query)
        org = org_schema.get_all_orgs(filters)
        result = []
        if org:
            serializer = OrgSerializer(org, many=True)
            for data in serializer.data:
                org_data = {'org': data}
                branch = org_schema.get_branch_by_org_id(data['id'])
                if branch:
                    org_branch = OrgBranchSerializer(branch, many=True)
                    org_data['org_branches'] = org_branch.data
                partner = org_schema.get_partner_by_org_id(data['id'])
                if partner:
                    org_partner = OrgPartnerSerializer(partner, many=True)
                    org_data['org_partners'] = org_partner.data
                result.append(org_data)
            return Response(result, status=status.HTTP_200_OK)


def check_for_valid_number(request):
    phone_number = request.query_params.get("phone_number", None)
    if phone_number:
        flag = is_valid_phone_number(phone_number)
        if flag:
            valid = org_schema.get_org_by_phone_number(phone_number)
            if valid:
                return Response({"error": "Mobile number already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"msg": "Mobile number is okay."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Mobile number is not valid."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Please provide mobile number."}, status=status.HTTP_400_BAD_REQUEST)


def check_for_valid_company_name(request):
    company_name = request.query_params.get("company_name", None)
    if company_name:
        valid = org_schema.get_org_by_company_name(company_name)
        if valid:
            return Response({"error": "Company name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"msg": "Company name is okay."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Please provide company name."}, status=status.HTTP_400_BAD_REQUEST)


def check_for_valid_company_address(request):
    company_address = request.query_params.get("company_address", None)
    if company_address:
        valid = org_schema.get_org_by_company_address(company_address)
        if valid:
            return Response({"error": "Company address already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"msg": "Company address is okay."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Please provide company address."}, status=status.HTTP_400_BAD_REQUEST)


def check_for_valid_gst_number(request):
    gst_number = request.query_params.get("gst_number", None)
    if gst_number:
        valid = org_schema.get_org_by_gst_number(gst_number)
        if valid:
            return Response({"error": "GST number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"msg": "GST number is okay."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Please provide GST number."}, status=status.HTTP_400_BAD_REQUEST)

      
def update_org(request, org_id):
    org_id = int(org_id)
    if 'org' in request.data:
        org_data = request.data['org']
        org = org_schema.update_org(org_data, org_id)
    if 'org_branches' in request.data:
        branch_data = request.data['org_branches']
        for branch in branch_data:
            if 'email' in branch:
                email = branch['email']
                role = 'branch_user'
                user = get_user(email)
                if user:
                    return Response({'error': 'User exists.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    branch['user'] = add_user(email, role)
                del branch['email']
            if 'id' in branch:
                org_branch = org_schema.update_org_branch(branch, branch['id'])
            else:
                branch['org_id'] = org_id
                org_branch = org_schema.create_org_branch(branch)
    if 'org_partners' in request.data:
        partner_data = request.data['org_partners']
        for partner in partner_data:
            if 'id' in partner:
                org_partner = org_schema.update_org_partner(partner, partner['id'])
            else:
                partner['org_id'] = org_id
                org_partner = org_schema.create_org_partner(partner)
    return Response({"msg": "Organization details has been updated."}, status=status.HTTP_200_OK)


def update_org_state(request, org_id):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            state = request.query_params.get("state", True)
            org = org_schema.get_org_by_id(org_id)
            org.enabled = state
            org.save()
            return Response({"msg": "Organization state has been changed."}, status=status.HTTP_200_OK)
        except:
            return Response({"msg": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)


def get_org_by_id(org_id):
    org = org_schema.get_org_by_id(org_id)
    org_data = {}
    if org:
        org_data['org'] = OrgSerializer(org).data
        branch = org_schema.get_branch_by_org_id(org.id)
        if branch:
            org_branch = OrgBranchSerializer(branch, many=True)
            org_data['org_branches'] = org_branch.data
        partner = org_schema.get_partner_by_org_id(org.id)
        if partner:
            org_partner = OrgPartnerSerializer(partner, many=True)
            org_data['org_partners'] = org_partner.data
        return Response(org_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Org does not exists"}, status=status.HTTP_400_BAD_REQUEST)
