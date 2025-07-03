import datetime

from django.db import models
from users.models import User


class Orgs(models.Model):
    id = models.AutoField(primary_key=True)
    company_email = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_address = models.CharField(max_length=200, null=True, unique=True)
    company_id = models.CharField(max_length=200, null=True, unique=True)
    tan_no = models.CharField(max_length=200, null=True)
    cin_no = models.CharField(max_length=200, null=True)
    registered_company_name = models.CharField(max_length=200, null=True)
    mobile_number = models.CharField(max_length=10, null=True, unique=True)
    gst_number = models.CharField(max_length=15, null=True, unique=True)
    aadhar_no = models.CharField(max_length=12, null=True, unique=True)
    pan_no = models.CharField(max_length=10, null=True)
    enabled = models.BooleanField(null=False, default=True)
    gst_verified = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
    logo_url = models.CharField(max_length=200, null=True)
    company_website = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "mi_orgs"


class OrgPartners(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(Orgs, on_delete=models.CASCADE)
    sr_no = models.IntegerField(null=True)
    name = models.CharField(max_length=200, null=True)
    designation = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    mobile_number = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "mi_org_partners"


class OrgBranches(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(Orgs, on_delete=models.CASCADE)
    branch_address = models.TextField(null=True)
    identification_id = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pan_no = models.CharField(max_length=10, null=True)
    tan_no = models.CharField(max_length=200, null=True)
    branch_name = models.TextField(null=True)

    class Meta:
        db_table = "mi_org_branches"
