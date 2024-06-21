from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import POD
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class PODSerializer(ModelSerializer):
    class Meta:
        model = POD
        fields = [
            'id', 'sr_no', 'employee_code', 'employee_name',
            'to_be_sent_to_e_name', 'secretary_code', 'address',
            'mobile_no', 'pod_number', 'desp_on', 'received_date',
            'pod_image'
        ]


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
