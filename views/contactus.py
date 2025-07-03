from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from models.contactus.schema import create_contactus
from users.models import User
from views.utils import format_and_send_mail


def contact_us(request):
    contact_details = request.data
    current_dt = datetime.now()
    contact_details['created_at'] = current_dt
    create_contactus(contact_details)

    # form email parameters
    context = {'name': contact_details['name'],
               'company_name': contact_details['company_name'],
               'company_email': contact_details['company_email'],
               'message': contact_details['message'],
               'country': contact_details['country']}
    template = "send_contactus_mail.html"
    # create list of admin users for email recipients
    to_email = list(User.objects.filter(user_role='admin').values_list('email', flat=True))
    subject = 'Made in India Label | Inquiry Request'
    cc_mail = ['madeinindia@qcin.org']

    # format email template & send mail
    format_and_send_mail(template, subject, context, to_email, cc_mail)

    return Response({"msg": "Thanks for contacting us. We will connect with you shortly."}, status=status.HTTP_200_OK)
