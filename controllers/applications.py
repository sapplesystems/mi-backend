import graphene
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from graphql_jwt.decorators import login_required
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
import views.file_upload as upload_view
import views.applications as application_view
from views.applications import ApplicationType
from models.applications.models import Applications
import models.applications.serializer as application_serializer


class Query(graphene.ObjectType):
    all_applications = graphene.List(ApplicationType,
                                     description='Return all applications')

    @login_required
    def resolve_user(self, info):
        return info.context.user

    @login_required
    def resolve_all_applications(self, info, **kwargs):
        return Applications.objects.filter(**kwargs).order_by('id').all()


class ProductApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        return application_view.apply_for_product(request)


class ProductItemsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, application_id):
        return application_view.register_product_items(request, application_id)


class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return upload_view.upload_file_to_s3(request)


class ApplicationItemView(APIView):

    def get(self, request, external_application_id, sequence_id):
        return application_view.get_product_details(request, external_application_id, sequence_id)


class ApplicationUniqueItemView(APIView):

    def get(self, request, external_application_id, sequence_id, item_key):
        return application_view.get_product_details(request, external_application_id, sequence_id, item_key)


class ApplicationFeedbackView(APIView):

    def post(self, request):
        return application_view.submit_feedback(request)


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, external_application_id):
        return application_view.update_application_status(request, external_application_id)


class ApplicationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    serializer_class = application_serializer.ApplicationSerializer

    def get_queryset(self):
        return application_view.get_applications(self.request)


class ApplicationDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, application_id):
        return application_view.get_application_details(application_id)


class ApplicationItemsView(APIView):

    def get(self, request, application_id):
        return application_view.get_application_items(request, application_id)


class UpdateApplicationItemView(APIView):

    def post(self, request, item_id):
        return application_view.update_application_item(request, item_id)


class SearchApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    pagination_class = PageNumberPagination

    def get(self, request, org_id):
        return application_view.search_application(request, org_id)


class SearchApplicationView_V2(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    pagination_class = PageNumberPagination

    def get(self, request):
        return application_view.search_application_v2(request)


class SearchApplicationItemView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, application_id):
        return application_view.search_application_item(request, application_id)


class IndiannessPercentageView(APIView):
    def post(self, request):
        return application_view.calculate_indian_percentage(request)


class ReviewApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        return application_view.review_application(request)


class ResubmitApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, application_id):
        return application_view.resubmit_application(request, application_id)


class CheckForApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, product_id):
        return application_view.check_for_application(request, product_id)


class GetApplicationStatsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        return application_view.get_applications_stats(request)


class AssignApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, application_id):
        return application_view.assign_application(request, application_id)


class UpdateApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, application_id):
        return application_view.update_application(request, application_id)
