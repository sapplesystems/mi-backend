from utils.db import get_db_rows
from .models import Applications, ApplicationItems, ApplicationDetails, ApplicationReview, ApplicationSupervisor
from .serializer import CreateApplicationSerializer, CreateApplicationDetailsSerializer, ApplicationFeedbacksSerializer, \
    UpdateApplicationDetailsSerializer
from django.db.models import Q


def create_application(application):
    serializer = CreateApplicationSerializer(data=application)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def insert_application_details(application_details):
    serializer = CreateApplicationDetailsSerializer(data=application_details)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def get_valid_application(application_id, applicant):
    return Applications.objects.filter(unique_application_id=application_id,
                                       applicant=applicant,
                                       status='approved').first()


def get_application(unique_application_id):
    return Applications.objects.filter(unique_application_id=unique_application_id).first()


def get_application_by_id(id):
    return Applications.objects.filter(id=id).first()


def bulk_insert_application_items(application_items):
    items = [ApplicationItems(**item) for item in application_items]
    ApplicationItems.objects.bulk_create(items)


def get_product_details(external_application_id, sequence_id, item_key=None):
    query_filter = {
        'application__unique_application_id': external_application_id,
        'sequence_id': sequence_id
    }
    if item_key is not None:
        query_filter['item_key'] = item_key
    return ApplicationItems.objects \
        .filter(**query_filter) \
        .first()


def product_item_exists(application_id, sequence_id, item_key):
    result = get_db_rows('''SELECT id FROM mi_application_items
                            WHERE application_id = %s
                                  AND sequence_id = %s
                                  AND item_key IS NOT DISTINCT FROM %s''',
                         (application_id, sequence_id, item_key))
    return result and len(result) > 0


def submit_feedback(feedback_details):
    serializer = ApplicationFeedbacksSerializer(data=feedback_details)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def check_filter(filters):
    if isinstance(filters, dict):
        query = Q(**filters)
    else:
        query = filters

    return query


def get_applications(filters):
    query = check_filter(filters)
    return Applications.objects.filter(query).order_by('-updated_at').all()


def get_application_details(filters):
    return ApplicationDetails.objects.filter(**filters).first()


def get_application_items(filters):
    query = check_filter(filters)
    return ApplicationItems.objects.filter(query).order_by('-updated_at').all()


def get_item_by_id(item_id):
    return ApplicationItems.objects.get(pk=item_id)


def add_application_review(data):
    product = ApplicationReview(**data).save()
    return product


def get_review_by_application_id(application_id):
    return ApplicationReview.objects.filter(application=application_id).last()


def update_application_details(result, application_details):
    serializer = UpdateApplicationDetailsSerializer(instance=result, data=application_details)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def get_application_details_by_application_id(application_id):
    return ApplicationDetails.objects.filter(application_id=application_id).first()


def add_application_supervisor(data):
    return ApplicationSupervisor.objects.update_or_create(application_id=data["application_id"], defaults=data)


def get_supervisor_by_application_id(application_id):
    return ApplicationSupervisor.objects.filter(application=application_id).last()


def update_application(data, application_id):
    application = Applications.objects.filter(id=application_id).update(**data)
    return application


def get_application_with_same_product(filters, application_id):
    query = check_filter(filters)
    return Applications.objects.exclude(id=application_id).filter(query).order_by('-updated_at').all()
