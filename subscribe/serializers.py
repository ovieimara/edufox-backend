from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Discount, Plan, Subscribe

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscribeSerializer(serializers.ModelSerializer):
    expiry_date = serializers.SerializerMethodField()
    class Meta:
        model = Subscribe

    def get_expiry_date(self, obj):
        return obj.get_expiry_date()



    

