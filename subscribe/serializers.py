from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Discount, Plan, Subscribe
from datetime import timedelta

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    class Meta:
        model = Plan
        fields = '__all__'
        ordering = ['amount']

    def get_amount(self, obj):
        return f"{obj.amount:,.2f}"

class SubscribeSerializer(serializers.ModelSerializer):
    # expiry_date = serializers.SerializerMethodField()
    # expiry_date = serializers.Ser
    class Meta:
        model = Subscribe
        fields = ['user', 'plan', 'grade', 'expiry_date']
        # depth = 1

    # def get_expiry_date(self, obj):
    #     #created + plan.duration
    #     return obj.created + timedelta(days=obj.plan.duration)

    # def get_expiry(self, obj):
    #     print(obj.plan.duration)
    #     return obj.get_expiry_date()



    

