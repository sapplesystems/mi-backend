import os
import re
import requests

from validate_email_address import validate_email


def is_valid_email(email):
    try:
        is_valid = validate_email(email, verify=True)
        return is_valid
    except Exception as e:
        return False


def is_valid_phone_number(phone_number):
    r = re.fullmatch('[6-9][0-9]{9}', phone_number)
    if r is not None:
        return True
    else:
        return False


def validate_captcha(token):
    secret_key = os.getenv("CAPTCHA_SECRET_KEY")

    # captcha verification
    data = {
        'response': token,
        'secret': secret_key
    }

    resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    return resp.json()
