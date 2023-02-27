from django.contrib.auth.models import User
from rest_framework import serializers
# from .validators import validate_username
from djoser.serializers import UserSerializer
from .models import (Message, Notify)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class NotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Notify
        fields = '__all__'


    # def updateMessage(self, obj):
    #     obj.updateMessage()
    #     return super().update(instance, validated_data)

