from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

from models.orgs.models import Orgs, OrgBranches
from models.products.models import Products


class Applications(models.Model):
    id = models.AutoField(primary_key=True)
    org = models.ForeignKey(Orgs, on_delete=models.CASCADE)
    unique_application_id = models.CharField(max_length=200, null=False, unique=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    status = models.TextField(null=True)
    application_date = models.DateTimeField(null=False)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)

    class Meta:
        db_table = "mi_applications"


class ApplicationDetails(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    category = models.CharField(max_length=100, null=True)
    is_product_regulated = models.BooleanField(null=True)
    regulated_product_details = models.JSONField(null=True)
    unregulated_product_details = models.JSONField(null=True)
    is_imported = models.BooleanField(null=True)
    product_details = models.JSONField(null=True)
    pricing = models.JSONField(null=True)
    compositions = models.JSONField(null=True)
    sm_process = models.JSONField(null=True)
    attachment_urls = ArrayField(models.CharField(max_length=300), blank=True, null=True)
    declaration = models.JSONField(null=True)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
    label_criteria = models.CharField(max_length=100, null=True)
    melted_criteria = models.CharField(max_length=100, null=True)
    value_addition = models.DecimalField(max_digits=20, decimal_places=5, null=True)
    attachments = models.JSONField(null=True)
    application_doc = models.CharField(null=True)

    class Meta:
        db_table = "mi_application_details"


class ApplicationItems(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    sequence_id = models.CharField(max_length=100)
    item_key = models.CharField(max_length=100, null=True)
    branch = models.ForeignKey(OrgBranches, on_delete=models.CASCADE, null=True)
    item_details = models.JSONField(null=True)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)

    class Meta:
        unique_together = [['application', 'product', 'sequence_id', 'item_key']]
        db_table = "mi_application_items"


class ApplicationFeedbacks(models.Model):
    id = models.AutoField(primary_key=True)
    application_item = models.ForeignKey(ApplicationItems, on_delete=models.CASCADE)
    feedback = models.TextField(null=False)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)

    class Meta:
        db_table = "mi_application_feedbacks"


class ApplicationReview(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    review_comment = models.TextField(null=False)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "mi_applications_review"


class ApplicationSupervisor(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='supervisor')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignee')

    class Meta:
        db_table = "mi_applications_reviewer"
