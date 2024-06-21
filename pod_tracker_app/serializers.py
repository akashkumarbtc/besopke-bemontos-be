# serializers.py
from rest_framework import serializers
from admin_app.models import POD


class PODSerializer(serializers.ModelSerializer):
    class Meta:
        model = POD
        fields = '__all__'
