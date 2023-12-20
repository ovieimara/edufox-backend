from rest_framework import serializers
from form.models import Waiter
from rest_framework.response import Response
from rest_framework import generics, status, mixins


class WaiterSerializer(serializers.ModelSerializer):
    # update = serializers.BooleanField(default=False)

    class Meta:
        model = Waiter
        fields = "__all__"

    def create(self, validated_data):
        data = {}
        email = validated_data.get('email')
        wait_queryset = Waiter.objects.filter(email=email)

        if wait_queryset.exists():
            response = super().update(wait_queryset.first(), validated_data)
            # print("response_exists: ", response, wait_queryset)
            data = {"email": response.email, "first_name": response.first_name,
                    "last_name": response.last_name, 'update': True}
            return data

        response = super().create(validated_data)
        data = {"email": response.email, "first_name": response.first_name,
                "last_name": response.last_name, 'update': False}
        return data
