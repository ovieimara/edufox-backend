from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TempStudent
User = get_user_model()

unique_user_email = UniqueValidator(queryset=User.objects.all(), lookup='iexact')

def validate_email(value):
    qs = User.objects.filter(email__iexact=value)
    if qs.exists():
        raise serializers.ValidationError(f"{value} already exists")
    return value

def validate_username(value):
    qs = TempStudent.objects.filter(username__iexact=value)
    if qs.exists():
        raise serializers.ValidationError(f"{value} already exists")
    return value