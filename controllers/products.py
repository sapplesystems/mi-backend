from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

import views.products as product_view


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return product_view.add_product(request.data)

class UpdateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        return product_view.update_product(request, product_id)


class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return product_view.search_product(request)


class GetAllProductsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        return product_view.get_all_products(request)


class GetAllCategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return product_view.get_categories(request)


