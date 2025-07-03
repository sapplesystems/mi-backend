from django.db import models


class verify_user(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=200, null=True)
    verification_code = models.CharField(max_length=200, null=True)
    expiry = models.DateTimeField(null=False)
    count = models.IntegerField(default=5, null=False)
    resend_flag = models.BooleanField(default=True)

    class Meta:
        db_table = "mi_verify_user"
