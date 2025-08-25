import os
import uuid
import logging
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage
from django.template.loader import get_template
from rest_framework import status
from rest_framework.response import Response
from graphene_django.types import DjangoObjectType
from django.db.models import Q

import models.orgs.schema as orgs_schema
import models.products.schema as product_schema
from models import applications
from models.applications.models import Applications, ApplicationSupervisor, ApplicationReview
from models.applications.models import ApplicationItems
import models.applications.schema as application_schema
import models.applications.serializer as application_serializer
from models.products.models import Products
from models.products.serializer import ProductSerializer
from models.verify_user.models import verify_user
from users.models import User
from views.utils import create_presigned_url, send_email, format_and_send_mail


class ApplicationType(DjangoObjectType):
    class Meta:
        model = Applications


def apply_for_product(request):
    kwargs = request.data
    product = kwargs.pop("product_id", None)
    if check_for_application(request, product).data is True:
        return Response({'error': "You have already applied for this product."}, status=status.HTTP_400_BAD_REQUEST)
    current_dt = datetime.now()
    # TODO: if kwargs contains id then API should update the existing application
    unique_application_id = uuid.uuid4().hex
    org = orgs_schema.get_org_by_user(request.user.id)
    if request.user.user_role == 'branch_user':
        org = orgs_schema.get_org_by_branch_user(request.user.id).org
    application = {
        'org': org.id,
        'unique_application_id': unique_application_id,
        'applicant': request.user.id,
        'product': product,
        'status': kwargs.pop("application_status", "draft"),
        'application_date': current_dt,
        'created_at': current_dt,
        'updated_at': current_dt,
    }
    result = application_schema.create_application(application)
    application_id = result.get('id', None)
    kwargs['application'] = application_id
    kwargs['created_at'] = current_dt
    kwargs['updated_at'] = current_dt
    application_schema.insert_application_details(kwargs)

    # form email parameters
    context = {'unique_application_id': unique_application_id}
    template = "application_created.html"
    to_email = [request.user.email]
    subject = 'Made in India Label | Application Created (Draft)'

    # format email template & send mail
    format_and_send_mail(template, subject, context, to_email)

    return Response({'id': application_id, 'external_id': unique_application_id}, status=status.HTTP_201_CREATED)


def get_item_url(request, application_id, sequence_id, item_key):
    request_meta = request.META
    url_scheme = request_meta['wsgi.url_scheme'] or 'http'
    host_url = f'{url_scheme}://{request_meta["HTTP_HOST"]}'
    item_url = f'{os.getenv("HOST_URL", host_url)}/product-details/{application_id}/{sequence_id}'
    if item_key:
        item_url += f'/{item_key}'
    return item_url


def register_product_items(request, external_application_id):
    user = request.user
    org = orgs_schema.get_org_by_user(user.id)
    if request.user.user_role == 'branch_user':
        org = orgs_schema.get_org_by_branch_user(request.user.id).org
    if org.enabled is False:
        return Response({"error": "You are not authorized user."}, status=status.HTTP_400_BAD_REQUEST)
    user_id = request.user.id
    
    valid_application = application_schema.get_valid_application(external_application_id, user_id)
    if valid_application is None:
        return Response({"error": "Given Application ID is invalid or pending for approval."},
                        status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    current_dt = datetime.now()
    product_items = []
    items_details = []
    if not isinstance(data, list):
        return Response({"error": "Incorrect data format. Data should be a list of item details."},
                        status=status.HTTP_400_BAD_REQUEST)
    for item in data:
        if not isinstance(item, dict):
            return Response({"error": "Incorrect item details format. Item details should be in dictionary format."},
                            status=status.HTTP_400_BAD_REQUEST)
        state = 'Created'
        sequence_id = item.pop("sequence_id", None) or uuid.uuid4().hex
        item_key = item.pop("item_key", None)
        p = product_schema.get_product(valid_application.product_id)
        product_details = {
            'application': valid_application,
            'product': p,
            'sequence_id': sequence_id,
            'item_key': item_key,
            'created_at': current_dt,
            'updated_at': current_dt,
        }
        if application_schema.product_item_exists(valid_application.id, sequence_id, item_key):
            state = 'Existed'
        if state != 'Existed' and 'hsn_code' in item.keys():
            if item['hsn_code'].find(str(p.hsn_code)) != 0:
                state = 'Error'
                item['msg'] = 'Invalid HSN Code'
        branch_id = item.get("branch_id", None)
        if branch_id:
            branch_details = orgs_schema.get_branch(branch_id)
            item['Address of Mfg. Unit'] = branch_details.branch_address if branch_details else ''
        product_details['item_details'] = item
        response_details = item.copy()
        response_details['state'] = state
        response_details['url'] = get_item_url(request, external_application_id, sequence_id,
                                               item_key) if state != 'Error' else None
        if state == 'Created':
            product_items.append(product_details)
        items_details.append(response_details)
    try:
        application_schema.bulk_insert_application_items(product_items)
    except Exception as error:
        logging.exception(error)
        return Response({'error': 'sequence_id already exists'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(items_details, status=status.HTTP_201_CREATED)


def get_product_details(request, external_application_id, sequence_id, item_key=None):
    branch_name = None
    product_obj = application_schema.get_product_details(external_application_id, sequence_id, item_key)
    if product_obj:
        application_details = application_schema.get_application_details({'application_id': product_obj.application.id})
        item_details = product_obj.item_details
        hsn_code = item_details.pop('hsn_code', product_obj.application.product.hsn_code)
        value_addition = application_details.value_addition or 100
        label_criteria = "Melted & poured" if application_details.label_criteria == 'melted_poured' else "Local value addition"
        mii_criteria = label_criteria + " (" + str(value_addition) + "%)"
        s3_url = os.getenv("S3_URL")  # TODO: ADD this in infra ENV
        company_logo = product_obj.application.org.logo_url
        if company_logo and s3_url:
            company_logo = s3_url + company_logo
        address = product_obj.application.org.company_address
        branch_name = None
        if product_obj.application.applicant.user_role == "branch_user":
            org_id = product_obj.application.org.id
            applicant_id = product_obj.application.applicant.id
            branch = orgs_schema.get_branch_by_org_id_applicant_id(org_id, applicant_id)
            address = branch.values('branch_address').first()['branch_address']
            branch_name = branch.values('branch_name').first()['branch_name']
        product_details = {
            "Company Name": product_obj.application.org.registered_company_name,
            "Branch Name": branch_name,
            "Company Website": product_obj.application.org.company_website,
            "Company ID": product_obj.application.org.id,
            "company_logo": company_logo,
            "Product": product_obj.application.product.name,
            "HSN Code": hsn_code,
            "Category": product_obj.application.product.category,
            "Description": product_obj.application.product.description,
            "MII Criteria": mii_criteria,
            "sequence_id": product_obj.sequence_id,
            "updated_at": product_obj.application.updated_at,
            "Address of Mfg. Unit": address
        }
        product_details.update(item_details)
        return Response(product_details, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid Application ID or Sequence ID."}, status=status.HTTP_400_BAD_REQUEST)


def submit_feedback(request):
    feedback_details = request.data
    external_application_id = feedback_details.pop("external_application_id", None)
    sequence_id = feedback_details.pop("sequence_id", None)
    application_item = application_schema.get_product_details(external_application_id, sequence_id)
    if application_item:
        current_dt = datetime.now()
        feedback_details['created_at'] = current_dt
        feedback_details['updated_at'] = current_dt
        feedback_details['application_item'] = application_item.id
        return Response(application_schema.submit_feedback(feedback_details), status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Invalid Application ID or Sequence ID."}, status=status.HTTP_400_BAD_REQUEST)


def update_application_status(request, external_application_id):
    if request.user.user_role not in ['supervisor']:
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    application_details = application_schema.get_application(external_application_id)
    if application_details:
        application_status = request.data.get("status")
        application_details.status = application_status
        application_details.updated_at = datetime.now()
        application_details.save()

        # form email parameters to send mail to applicant
        context = {'unique_application_id': application_details.unique_application_id,
                   'application_status': application_status}
        template = "final_status_to_applicant.html"
        to_email = [application_details.applicant.email]
        subject = 'Made in India Label | ApplicationStatus Update of Application ID: ' + str(application_details.unique_application_id)

        # format email template & send mail to applicant
        format_and_send_mail(template, subject, context, to_email)

        return Response({'msg': 'Status updated successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid Application ID."}, status=status.HTTP_400_BAD_REQUEST)


def get_applications(request):
    filter = {}
    if request.user.is_staff:
        return application_schema.get_applications(filter)
    else:
        filter['applicant'] = request.user
        return application_schema.get_applications(filter)


def get_application_details(application_id):
    result = application_schema.get_application_details({'application_id': application_id})
    data = application_serializer.ApplicationDetailsSerializer(result).data

    review = application_schema.get_review_by_application_id(data['application']['id'])
    if review:
        data['review_comment'] = review.review_comment

    composition = data["compositions"]
    if composition:
        for composition in data["compositions"]:
            if "files" in composition:
                for i, file_url in enumerate(composition["files"]):
                    signed_url = create_presigned_url(os.getenv("S3_BUCKET"), file_url)
                    composition["files"][i] = signed_url

    sm_process = data["sm_process"]
    if sm_process:
        sm_process = data.get("sm_process", {})
        sm_process_files = sm_process.get("files", [])

        if sm_process_files:
            for i, file_url in enumerate(sm_process_files):
                signed_url = create_presigned_url(os.getenv("S3_BUCKET"), file_url)
                sm_process_files[i] = signed_url

            sm_process["files"] = sm_process_files
            data["sm_process"] = sm_process

    attachments = data.get("attachments", {})
    if attachments:
        for attachment_key, attachment_value in attachments.items():
            files = attachment_value
            if files:
                for i, file_url in enumerate(files):
                    signed_url = create_presigned_url(os.getenv("S3_BUCKET"), file_url)
                    files[i] = signed_url

    application_doc = data['application_doc']
    if application_doc:
        signed_url = create_presigned_url(os.getenv("S3_BUCKET"), application_doc)
        data['application_doc'] = signed_url

    return Response(data, status=status.HTTP_200_OK)


def get_application_items(request, application_id):
    filters = {'application_id': application_id}
    product_items = application_schema.get_application_items(filters)
    application = application_schema.get_application_by_id(application_id)
    external_application_id = application.unique_application_id
    items = [application_serializer.ApplicationItemsSerializer(product_item).data
             for product_item in product_items]
    for item in items:
        item['url'] = get_item_url(request, external_application_id, item['sequence_id'],
                                   item['item_key'] if item['item_key'] else None)
    return Response(items, status=status.HTTP_200_OK)


def update_application_item(request, item_id):
    try:
        item_details = request.data
        product_item = application_schema.get_item_by_id(item_id)
        product_item.item_details = item_details
        product_item.updated_at = datetime.now()
        product_item.save()
        return Response({"msg": "Product item details updated successfully"},
                        status=status.HTTP_200_OK)
    except:
        return Response({"error": "Item id doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


def search_application(request, org_id):
    query = request.query_params.get("query", "")
    page_number = request.query_params.get("page", 1)
    items_per_page = 10
    user = request.user.is_staff
    if user is False:
        filters = Q(Q(applicant_id=request.user.id) & Q(product__name__icontains=query))
    else:
        filters = Q(product__name__icontains=query) | Q(org__registered_company_name__icontains=query) | Q(
            unique_application_id=query)
    queryset = application_schema.get_applications(filters)
    paginator = Paginator(queryset, items_per_page)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return Response({'message': 'No more pages available'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = application_serializer.ApplicationSerializer(page, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def search_application_v2(request):
    query = request.query_params.get("query", "")
    app_status = request.query_params.get("status", None)
    page_number = request.query_params.get("page", 1)
    state = request.query_params.get("state", None)
    filters = Q()
    if state and (state in ['assigned', 'unassigned']):
        assigned_id = list(ApplicationSupervisor.objects.all().values_list('application_id', flat=True))
        if state == 'assigned':
            filters &= Q(id__in=assigned_id)
        else:
            filters &= ~Q(id__in=assigned_id)
    items_per_page = 10
    user_role = request.user.user_role
    if user_role in ['admin', 'super_admin']:
        filters &= Q(Q(product__name__icontains=query) | Q(org__registered_company_name__icontains=query)
                     | Q(unique_application_id__icontains=query))
        filters &= ~Q(status='draft')
    elif user_role in ['supervisor']:
        user_id = request.user.id
        supervisor_id = list(
            ApplicationSupervisor.objects.filter(reviewer_id=user_id).values_list('application_id', flat=True))
        filters &= Q(Q(id__in=supervisor_id) & Q(
            Q(product__name__icontains=query) | Q(org__registered_company_name__icontains=query) | Q(unique_application_id__icontains=query)))
        filters &= ~Q(status='draft')
    elif user_role in ['org_admin', 'applicant']:
        org = orgs_schema.get_org_by_user(request.user.id).id
        filters &= Q(org_id=org) & Q(unique_application_id__icontains=query) & Q(applicant_id=request.user.id)
    elif user_role in ['branch_user']:
        applicant_id = request.user.id
        filters &= Q(applicant_id=applicant_id) & Q(unique_application_id__icontains=query)
    if app_status != "all" and app_status is not None:
        filters &= Q(status=app_status)
    queryset = application_schema.get_applications(filters)
    total_count = queryset.count()
    paginator = Paginator(queryset, items_per_page)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return Response({'message': 'No more pages available'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = application_serializer.ApplicationSerializer(page, many=True)
    for data in serializer.data:
        review = application_schema.get_review_by_application_id(data['id'])
        if review:
            data['review_comment'] = review.review_comment
        supervisor = application_schema.get_supervisor_by_application_id(data['id'])
        if supervisor:
            supervisor_data = {'supervisor_id': supervisor.reviewer.id,
                               'supervisor_name': supervisor.reviewer.username}
            data['supervisor'] = supervisor_data
    result_data = {'applications': serializer.data, 'total_count': total_count}
    return Response(result_data, status=status.HTTP_200_OK)


def search_application_item(request, application_id):
    query = request.query_params.get("query", "")
    multiple_query = Q(
        (Q(application_id=application_id) & Q(sequence_id__icontains=query)) |
        (Q(application_id=application_id) & Q(item_key__icontains=query)))
    result = application_schema.get_application_items(multiple_query)
    return Response([application_serializer.ApplicationItemsSerializer(application).data
                     for application in result],
                    status=status.HTTP_200_OK)


def calculate_indian_percentage(request):
    data = request.data

    if not data:
        return Response({'error': "Compositions cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    total_cost = 0
    domestic_cost = 0

    for item in data:
        total_cost += float(
            item.get("total_price", 0))

        if item.get("is_imported", "") == "Domestic":
            domestic_cost += float(item.get("total_price", 0))

    indian_percentage = (domestic_cost / total_cost) * 100

    return Response(format(indian_percentage, ".2f"), status=status.HTTP_200_OK)


def review_application(request):
    if request.user.user_role not in ['supervisor']:
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    review_details = request.data
    application = review_details.get("application_id", None)
    review_comment = review_details.get("review_comment", None)
    current_dt = datetime.now()
    review_details['reviewer'] = request.user
    review_details["created_at"] = current_dt
    review_details["updated_at"] = current_dt
    application_details = application_schema.get_application_by_id(application)
    if application_details:
        review = application_schema.add_application_review(review_details)
        application_details.status = "changeRequest"
        application_details.updated_at = datetime.now()
        application_details.save()

        # form email parameters to send mail to applicant
        context = {'unique_application_id': application_details.unique_application_id,
                   'review_comment': review_comment}
        template = "change_request_to_applicant.html"
        to_email = [application_details.applicant.email]
        subject = 'Made in India Label | Application Reviewed'

        # format email template & send mail to applicant
        format_and_send_mail(template, subject, context, to_email)

        return Response("Application has been sent to review", status=status.HTTP_200_OK)
    else:
        return Response("Application not found", status=status.HTTP_404_NOT_FOUND)


def resubmit_application(request, application_id):
    kwargs = request.data
    current_dt = datetime.now()
    kwargs['updated_at'] = current_dt
    result = application_schema.get_application_details_by_application_id(application_id)
    if result:
        application_schema.update_application_details(result, kwargs)
        app_result = application_schema.get_application_by_id(application_id)
        app_result.status = kwargs['application_status']
        app_result.save()
        applicant_mail = request.user.email
        context = {'unique_application_id': app_result.unique_application_id}
        template = get_template("resubmit_to_applicant.html").render(context)
        data = {
            'subject': 'Made in India Label | Application Re-Submitted ',
            'body': result,
            'to_email': applicant_mail,
            'html_message': template
        }
        response = send_email(data)
        return Response("Application Resubmitted.", status=status.HTTP_200_OK)
    else:
        return Response("Application not found", status=status.HTTP_404_NOT_FOUND)


def check_for_application(request, product_id):
    filters = {'applicant_id': request.user.id, 'product_id': product_id}
    product_items = application_schema.get_applications(filters)
    return Response(bool(product_items), status=status.HTTP_200_OK)


def get_applications_stats(request):
    if request.user.user_role in ['admin', 'super_admin']:
        submitted = Applications.objects.all().count()
        approved = Applications.objects.filter(status="approved").count()
        rejected = Applications.objects.filter(status="rejected").count()
        result = {"submitted": submitted, "approved": approved, "rejected": rejected}
        return Response(result, status=status.HTTP_200_OK)
    elif request.user.user_role == 'ministry':
        submitted = Applications.objects.all().count()
        approved = Applications.objects.filter(status="approved").count()
        rejected = Applications.objects.filter(status="rejected").count()
        users_registered = User.objects.all().count()
        users_visited = verify_user.objects.all().count()
        result = {"users_registered": users_registered, "users_visited": users_visited, "submitted": submitted,
                  "approved": approved, "rejected": rejected}
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)


# assign application to supervisor to review
def assign_application(request, application_id):
    if request.user.user_role not in ['admin', 'super_admin']:
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = request.data
        data["application_id"] = application_id
        data["assigned_by_id"] = request.user.id
        data["reviewer_id"] = data['reviewer_id']
        current_dt = datetime.now()
        data["created_at"] = current_dt
        data["updated_at"] = current_dt
        obj_store, created = application_schema.add_application_supervisor(data)

        # form email parameters to send mail to supervisor
        app_result = application_schema.get_application_by_id(application_id)
        context = {'unique_application_id': app_result.unique_application_id}
        template = "assign_application_to_supervisor.html"
        # get reviewer email id from reviewer_id
        reviewer_mail = User.objects.filter(id=data['reviewer_id']).values_list('email', flat=True).first()
        to_email = [reviewer_mail]
        subject = 'Made in India Label | Application Assigned to Review'

        # format email template & send mail to supervisor
        format_and_send_mail(template, subject, context, to_email)

        return Response({"msg": "Application has been assigned to Supervisor."}, status=status.HTTP_200_OK)


def update_application(request, application_id):
    kwargs = request.data

    # check if existing applications registered with the same product
    if check_for_application_with_same_product(request, request.data['product_id'], application_id).data is True:
        return Response({'error': "You have already applied for this product."}, status=status.HTTP_400_BAD_REQUEST)

    # check verification doc is required when label_criteria is melted_poured and application_status not in draft state
    if kwargs['label_criteria'] == "melted_poured" and kwargs['application_status'] not in ['draft', 'changeRequest'] \
            and ('application_doc' not in kwargs or
                 kwargs['application_doc'] is None or
                 kwargs['application_doc'] == ""):
        return Response({"error": "Verification document is required."}, status=status.HTTP_400_BAD_REQUEST)

    current_dt = datetime.now()
    kwargs['updated_at'] = current_dt
    app = {'updated_at': current_dt, 'product_id': request.data['product_id']}
    application = application_schema.update_application(app, application_id)
    result = application_schema.get_application_details_by_application_id(application_id)
    if result:
        application_schema.update_application_details(result, kwargs)
        if 'application_status' in request.data:
            app_result = application_schema.get_application_by_id(application_id)
            app_result.status = request.data['application_status']
            app_result.save()

            if request.data['application_status'] == 'submitted':
                # form email parameters to send mail to applicant
                context = {'unique_application_id': app_result.unique_application_id}
                template = "application_submitted_to_applicant.html"
                to_email = [request.user.email]
                subject = 'Made in India Label | Application Submitted'

                # format email template & send mail to applicant
                format_and_send_mail(template, subject, context, to_email)

                # form email parameters to send mail to all admins
                context = {'unique_application_id': app_result.unique_application_id}
                template = "application_submitted_to_admins.html"
                to_email = list(User.objects.filter(user_role='admin').values_list('email', flat=True))
                subject = 'Made in India Label | Application Submitted'

                # format email template & send mail to all admins
                format_and_send_mail(template, subject, context, to_email)

            if request.data['application_status'] == 'resubmitted':
                # form email parameters to send mail to supervisor
                context = {'unique_application_id': app_result.unique_application_id}
                template = "application_resubmitted.html"
                # get reviewer mail id
                reviewer_id = ApplicationReview.objects.filter(application_id=app_result.id).values_list('reviewer', flat=True).first()
                reviewer_mail = User.objects.filter(id=reviewer_id).values_list('email', flat=True).first()
                to_email = [reviewer_mail]
                subject = 'Made in India Label | Application Re-Submitted'

                # format email template & send mail to supervisor
                format_and_send_mail(template, subject, context, to_email)

        return Response({"msg": "Application Updated."}, status=status.HTTP_200_OK)
    else:
        return Response({"msg": "Application not found"}, status=status.HTTP_404_NOT_FOUND)


def check_for_application_with_same_product(request, product_id, application_id):
    filters = {'applicant_id': request.user.id, 'product_id': product_id}
    product_items = application_schema.get_application_with_same_product(filters, application_id)
    return Response(bool(product_items), status=status.HTTP_200_OK)
