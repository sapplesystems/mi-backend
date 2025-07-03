from django.db import models


class contactus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False)
    company_name = models.CharField(null=False)
    company_email = models.CharField(null=False)
    message = models.CharField(null=False)
    country = models.CharField(null=False)
    created_at = models.DateTimeField(null=False)

    class Meta:
        db_table = "mi_contactus"
