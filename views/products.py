from datetime import datetime

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

import utils.csv as csv_utils
import models.products.schema as product_schema
from models.products.models import Products
from models.products.serializer import ProductSerializer, CategorySerializer


def add_product(data):
    current_dt = datetime.now()
    data["created_at"] = current_dt
    data["updated_at"] = current_dt
    product = product_schema.add_product(data)
    if product:
        return Response({"msg": "Product has been added."}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "There is a problem in adding product."}, status=status.HTTP_400_BAD_REQUEST)


def search_product(request):
    query = request.query_params.get("query", "")
    products = [ProductSerializer(product).data for product in product_schema.search_product(query)]
    return Response(products, status=status.HTTP_200_OK)


def update_product(request, product_id):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = request.data
        updated_at = datetime.now()
        data["updated_at"] = updated_at
        product = product_schema.update_product(data, product_id)
        return Response({"msg": "Product has been updated."}, status=status.HTTP_200_OK)


def upload_products(csv_file):
    csv_data = csv_utils.read_csv(csv_file)
    current_dt = datetime.now()
    for data in csv_data:
        data["created_at"] = current_dt
        data["updated_at"] = current_dt
    product_schema.bulk_insert_products(csv_data)
    return None


def get_all_products(request):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        query = request.query_params.get("query", "")
        page_number = request.query_params.get("page", 1)
        items_per_page = 10
        filters = Q(name__icontains=query) | Q(category__icontains=query) | Q(hsn_code__icontains=query)
        queryset = product_schema.get_all_products(filters)
        if len(queryset) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if queryset:
                total_count = queryset.count()
                paginator = Paginator(queryset, items_per_page)
                try:
                    page = paginator.page(page_number)
                except EmptyPage:
                    return Response({'message': 'No more pages available'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = ProductSerializer(page, many=True)
                result_data = {'products': serializer.data, 'total_count': total_count}
                return Response(result_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': "Product does not exists"}, status=status.HTTP_400_BAD_REQUEST)


def get_categories(request):
    if request.user.user_role != 'super_admin':
        return Response({"error": "You are not authorized for this action."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        queryset = Products.objects.all().distinct('category')
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
