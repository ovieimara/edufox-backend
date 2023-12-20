from datetime import datetime, timedelta
from rest_framework import serializers

from student.validators import validate_email
from .models import Contact, ContactForm


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"

    def create(self, validated_data):
        data = {}
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        message = validated_data.get('message')

        queryset = ContactForm.objects.filter(email=email, message=message)
        if queryset.exists():
            return super().update(queryset.first(), validated_data)

        return super().create(validated_data)
