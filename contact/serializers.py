from datetime import datetime, timedelta
from rest_framework import serializers
from .models import Contact, ContactForm


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = "__all__"
