import os
import base64
from .models import POD
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer


class PODSerializer(serializers.ModelSerializer):
    pod_image_binary = serializers.SerializerMethodField()

    class Meta:
        model = POD
        fields = [
            'id', 'sr_no', 'employee_code', 'employee_name',
            'to_be_sent_to_e_name', 'secretary_code', 'address',
            'mobile_no', 'pod_number', 'desp_on', 'received_date',
            'pod_image', 'pod_image_binary'
        ]

    def get_pod_image_binary(self, obj):
        if obj.pod_image:
            return base64.b64encode(obj.pod_image).decode('utf-8')
        return None

    def validate_pod_image(self, value):
        if isinstance(value, bytes):
            return value
        elif value is None:
            return None
        raise serializers.ValidationError(
            "Invalid image format. Must be binary data.")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'pod_image' in data:
            del data['pod_image']  # Remove pod_image field from output
        return data

    def create(self, validated_data):
        # Handle pod_image separately if needed
        pod_image = validated_data.pop('pod_image', None)
        instance = super().create(validated_data)
        if pod_image:
            instance.pod_image = pod_image  # Assuming pod_image is binary data
            instance.save()
        return instance

    def update(self, instance, validated_data):
        # Handle pod_image separately if needed
        pod_image = validated_data.pop('pod_image', None)
        instance = super().update(instance, validated_data)
        if pod_image:
            instance.pod_image = pod_image  # Assuming pod_image is binary data
            instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    raise serializers.ValidationError("User is deactivated.")
            else:
                raise serializers.ValidationError(
                    "Unable to login with given credentials.")
        else:
            raise serializers.ValidationError(
                "Must provide username and password.")

        return data
