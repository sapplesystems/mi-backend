from django.db import models


class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)
    description = models.TextField(null=True)
    category = models.TextField(null=True)
    category_code = models.TextField(null=True)
    hsn_code = models.TextField(null=True)
    meta = models.JSONField(null=True)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)

    class Meta:
        db_table = "mi_products"
