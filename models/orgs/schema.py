from .models import Orgs, OrgPartners, OrgBranches
from models.orgs.serializer import OrgSerializer
from ..applications.schema import check_filter


def get_org_by_user(user_id):
    return Orgs.objects.filter(user=user_id).first()


def get_org_by_branch_user(user_id):
    return OrgBranches.objects.filter(user=user_id).first()


def get_org_by_phone_number(phone_number):
    return Orgs.objects.filter(mobile_number=phone_number).first()


def get_org_by_company_name(company_name):
    return Orgs.objects.filter(registered_company_name=company_name).first()


def get_org_by_company_address(company_address):
    return Orgs.objects.filter(company_address=company_address).first()


def get_org_by_gst_number(gst_number):
    return Orgs.objects.filter(gst_number=gst_number).first()


def register_org(org_data):
    serializer = OrgSerializer(data=org_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def register_org_partners(partners, org_id):
    instance = []
    for i in partners:
        i['org_id'] = org_id
        i.pop('key', None)
        instance.append(OrgPartners(**i))
    OrgPartners.objects.bulk_create(instance)


def register_org_branches(branches, org_id):
    instance = []
    for i in branches:
        i['org_id'] = org_id
        i.pop('key', None)
        instance.append(
            OrgBranches(**i))
    OrgBranches.objects.bulk_create(instance)


def get_branch(branch_id):
    return OrgBranches.objects.get(pk=branch_id)


def update_org_logo_url_schema(org_id, logo_url):
    org = Orgs.objects.filter(id=org_id).update(logo_url=logo_url)
    return org


def get_all_orgs(filters):
    query = check_filter(filters)
    return Orgs.objects.filter(query).order_by('-updated_at').all()


def update_org(data, org_id):
    org = Orgs.objects.filter(id=org_id).update(**data)
    return org


def get_branch_by_org_id(org_id):
    return OrgBranches.objects.filter(org=org_id)


def get_branch_by_org_id_applicant_id(org_id, applicant_id):
    return OrgBranches.objects.filter(org=org_id).filter(user=applicant_id)


def get_partner_by_org_id(org_id):
    return OrgPartners.objects.filter(org=org_id)


def update_org_branch(data, branch_id):
    org_branch = OrgBranches.objects.filter(id=branch_id).update(**data)
    return org_branch


def create_org_branch(data):
    org_branch = OrgBranches.objects.create(**data)
    return org_branch


def update_org_partner(data, partner_id):
    org_partner = OrgPartners.objects.filter(id=partner_id).update(**data)
    return org_partner


def create_org_partner(data):
    org_partner = OrgPartners.objects.create(**data)
    return org_partner


def get_org_by_id(org_id):
    return Orgs.objects.filter(id=org_id).first()
