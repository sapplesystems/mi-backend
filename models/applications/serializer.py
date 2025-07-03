from rest_framework import serializers

from .models import Applications, ApplicationDetails, ApplicationItems, ApplicationFeedbacks
from models.orgs.serializer import OrgSerializer
from models.products.serializer import ProductSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    org = OrgSerializer()
    product = ProductSerializer()

    class Meta:
        model = Applications
        fields = ['id', 'unique_application_id', 'status',
                  'application_date', 'org', 'product', 'created_at', 'updated_at']


class CreateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications
        fields = '__all__'


class ApplicationDetailsSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer()

    class Meta:
        model = ApplicationDetails
        fields = ['id', 'application', 'description',
                  'category', 'is_product_regulated',
                  'regulated_product_details', 'unregulated_product_details',
                  'is_imported', 'product_details',
                  'pricing', 'compositions',
                  'sm_process', 'attachment_urls',
                  'declaration', 'created_at',
                  'updated_at', 'label_criteria', 'melted_criteria', 'attachments', 'application_doc']


class CreateApplicationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = '__all__'


class ApplicationItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationItems
        fields = '__all__'


class ApplicationFeedbacksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFeedbacks
        fields = '__all__'


class UpdateApplicationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = ['description',
                  'category', 'is_product_regulated',
                  'regulated_product_details', 'unregulated_product_details',
                  'is_imported', 'product_details',
                  'pricing', 'compositions',
                  'sm_process', 'attachment_urls',
                  'declaration',
                  'updated_at', 'label_criteria', 'melted_criteria', 'attachments',
                  'application_doc']
