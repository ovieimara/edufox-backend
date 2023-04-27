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
    # amount = serializers.SerializerMethodField()
    class Meta:
        model = Plan
        fields = '__all__'
        ordering = ['amount']

    def get_amount(self, obj):
        return f"{obj.amount:,.2f}"
    
    def validate_amount(self, value):
        value = value.replace(",", "")
        return f"{float(value):,.2f}"

class SubscribeSerializer(serializers.ModelSerializer):
    # expiry_date = serializers.SerializerMethodField()
    # expiry_date = serializers.Ser
    class Meta:
        model = Subscribe
        fields = ['user', 'grade', 'product', 'payment_method', 'expiry_date']
        # depth = 1

    def create(self, validated_data):
        payment_method = validated_data.get('payment_method')
        user = validated_data.get('payment_method')
        grade = validated_data.get('grade')
        if payment_method:
            subscribe = Subscribe.objects.filter(payment_method=payment_method)
            if subscribe.exists():
                subscriber = subscribe.first()
                
                if not user:
                    validated_data['user'] = subscriber.user

                if not grade:
                    validated_data['grade'] = subscriber.grade
                
                return super().update(subscriber, validated_data)
            
        return super().create(validated_data)

class InAppPaymentSerializer(serializers.ModelSerializer):
    # PAYMENT_METHOD_CHOICES = [
    #     (payment.id, payment.name) for payment in InAppPayment.objects.all()
    # ]
    # payment = serializers.ChoiceField(InAppPayment, '')
    class Meta:
        model = InAppPayment
        fields = '__all__'

    def validate_amount(self, value):
        if InAppPayment.objects.filter(amount=value).exists():
            raise serializers.ValidationError('amount field must be unique.')
        return value
    
    # def validate_transaction_id(self, value):
    #     if InAppPayment.objects.filter(transaction_id=value).exists():
    #         raise serializers.ValidationError('transaction_id field must be unique.')
    #     return value
    
    def create(self, validated_data):
        # print('validated_data: ', validated_data)
        transaction_id = validated_data.get('transaction_id')
        if transaction_id:
            # print('transaction_id: ', transaction_id)
            payment = InAppPayment.objects.filter(transaction_id=transaction_id)
            if payment.exists():
                return super().update(payment.first(), validated_data)
        return super().create(validated_data)

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
    # def validate_transaction_id(self, value):
    #     if AppleNotify.objects.filter(transaction_id=value).exists():
    #         raise serializers.ValidationError('transaction_id field must be unique.')
    #     return value

    def create(self, validated_data):
        transaction_id = validated_data.get('transaction_id')
        if transaction_id:
            payment = AppleNotify.objects.filter(transaction_id=transaction_id)
            if payment.exists():
                return super().update(payment.first(), validated_data)
        return super().create(validated_data)


class AndroidNotifySerializer(serializers.ModelSerializer):

    class Meta:
        model = AndroidNotify
        fields = '__all__'

    # def validate_transaction_id(self, value):
    #     if AndroidNotify.objects.filter(transaction_id=value).exists():
    #         raise serializers.ValidationError('transaction_id field must be unique.')
    #     return value
    
    def create(self, validated_data):
        # print('validated_data: ', validated_data)
        transaction_id = validated_data.get('transaction_id')
        if transaction_id:
            payment = AndroidNotify.objects.filter(transaction_id=transaction_id)
            if payment.exists():
                return super().update(payment.first(), validated_data)
        return super().create(validated_data)



    

