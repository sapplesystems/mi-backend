from rest_framework import serializers
from .models import Orgs, OrgPartners, OrgBranches


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orgs
        fields = '__all__'


class OrgPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgPartners
        fields = '__all__'


class OrgBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgBranches
        fields = '__all__'
