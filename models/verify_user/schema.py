from models.verify_user.models import verify_user


# return if verification code exists for specified email
def get_user_verification_code(email, code, now):
    return verify_user.objects.filter(email=email, verification_code=code, expiry__gt=now, count__gt=0).first()


def check_mail_sent_to_user(email, now):
    return verify_user.objects.filter(email=email, expiry__gt=now, count__gt=0).first()


def check_mail_resent_to_user(email):
    return verify_user.objects.filter(email=email, resend_flag=False).first()


def decrease_user_verification_code_check_count(email, now):
    verify = verify_user.objects.filter(email=email, expiry__gt=now).first()
    verify.count = verify.count - 1
    verify.save()
    return verify.count
