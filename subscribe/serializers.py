from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (Discount, Plan, Subscribe, InAppPayment, Product, 
                     AppleNotify, AndroidNotify)
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
        fields = ['user', 'grade', 'product', 'payment_method', 'expiry_date']
        # depth = 1

class InAppPaymentSerializer(serializers.ModelSerializer):
    # PAYMENT_METHOD_CHOICES = [
    #     (payment.id, payment.name) for payment in InAppPayment.objects.all()
    # ]
    # payment = serializers.ChoiceField(InAppPayment, '')
    class Meta:
        model = InAppPayment
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(write_only=True)
    # platform = serializers.CharField(write_only=True)
    class Meta:
        model = Product
        fields = '__all__'
        # extra_kwargs = {'name': {'write_only': True}, 
        # 'platform': {'write_only': True}
        # }

class AppleNotifySerializer(serializers.ModelSerializer):

    class Meta:
        model = AppleNotify
        fields = '__all__'


class AndroidNotifySerializer(serializers.ModelSerializer):

    class Meta:
        model = AndroidNotify
        fields = '__all__'



    

