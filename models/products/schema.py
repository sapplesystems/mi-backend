from django.db.models import Q, CharField, TextField
from django.db.models.functions import Length

from .models import Products
from ..applications.schema import check_filter

TextField.register_lookup(Length)


def add_product(data):
    try:
        product = Products(**data).save()
        return True
    except:
        return False


def get_product(product_id):
    return Products.objects.get(pk=product_id)


def search_product(query):
    return Products.objects \
        .filter(Q(name__icontains=query) | Q(hsn_code__icontains=query)) \
        .filter(hsn_code__length__gt=3) \
        .order_by('hsn_code') \
        .all()


def bulk_insert_products(application_items):
    items = [Products(**item) for item in application_items]
    Products.objects.bulk_create(items)


def update_product(data, product_id):
    product = Products.objects.filter(id=product_id).update(**data)
    return product


def get_all_products(filters):
    query = check_filter(filters)
    return Products.objects.filter(query).order_by('-updated_at').all()
