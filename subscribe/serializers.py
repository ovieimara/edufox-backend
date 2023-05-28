
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (Discount, Plan, Subscribe, InAppPayment, Product,
                     AppleNotify, AndroidNotify, GradePack)
from datetime import timedelta
from rest_framework.validators import UniqueTogetherValidator


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'


class PlanSerializer(serializers.ModelSerializer):
    # amount = serializers.SerializerMethodField()
    platform = serializers.CharField(default="")

    class Meta:
        model = Plan
        fields = '__all__'
        ordering = ['amount']

    def get_amount(self, obj):
        return f"{obj.amount:,.2f}"

    def validate_amount(self, value):
        value = value.replace(",", "")
        # return f"{float(value):,.2f}"
        return value


class SubscribeSerializer(serializers.ModelSerializer):
    # expiry_date = serializers.SerializerMethodField()
    # expiry_date = serializers.Ser
    class Meta:
        model = Subscribe
        fields = ['user', 'grade', 'product', 'payment_method']
        # depth = 1

    def create(self, validated_data):
        payment_method = validated_data.get('payment_method')
        user = validated_data.get('user')
        grade = validated_data.get('grade')
        if payment_method:
            subscribe = Subscribe.objects.filter(payment_method=payment_method)
            if subscribe.exists():
                subscriber = subscribe.first()
                subscribed_user = subscriber.user
                subscribed_grade = subscriber.grade
                # printOutLogs('PURCHASE7: ', subscribed_user)
                # printOutLogs('PURCHASE8: ', subscribed_grade)
                if not user and subscribed_user:
                    validated_data['user'] = subscribed_user

                if not grade and subscribed_grade:
                    validated_data['grade'] = subscribed_grade

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
            payment = InAppPayment.objects.filter(
                transaction_id=transaction_id)
            if payment.exists():
                return super().update(payment.first(), validated_data)
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(write_only=True)
    # platform = serializers.CharField(write_only=True)
    NAME_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Yearly', 'Yearly'),
    ]
    PRODUCT_CHOICES = [
        ('com.edufox.sub.autorenew.monthly', 'com.edufox.sub.autorenew.monthly'),
        ('com.edufox.sub.autorenew.quarterly',
         'com.edufox.sub.autorenew.quarterly'),
        ('com.edufox.sub.autorenew.yearly', 'com.edufox.sub.autorenew.yearly'),
        ('com.edufox.sub.flutterwave.autorenew.monthly',
         'com.edufox.sub.flutterwave.autorenew.monthly'),
        ('com.edufox.sub.flutterwave.autorenew.quarterly',
         'com.edufox.sub.flutterwave.autorenew.quarterly'),
        ('com.edufox.sub.flutterwave.autorenew.yearly',
         'com.edufox.sub.flutterwave.autorenew.yearly')
    ]

    AMOUNT_CHOICES = [
        ('5500.00', '5500.00'),
        ('12000.00', '12000.00'),
        ('35000.00', '35000.00'),
    ]

    CURRENCY_CHOICES = [
        ('₦', '₦'),
        ('$', '$'),
        ('£', '£'),
        ('€', '€'),
    ]

    PLATFORM_CHOICES = [
        ('android', 'android'),
        ('in-app', 'in-app'),
        ('ios', 'ios'),
        ('flutterwave web', 'flutterwave web'),
        ('flutterwave app', 'flutterwave app'),
    ]

    name = serializers.ChoiceField(
        choices=NAME_CHOICES, allow_blank=True, allow_null=True, default=dict)

    product_id = serializers.ChoiceField(
        choices=PRODUCT_CHOICES, allow_blank=True, allow_null=True, default=dict)

    amount = serializers.ChoiceField(
        choices=AMOUNT_CHOICES, allow_blank=True, allow_null=True, default=dict)

    currency = serializers.ChoiceField(
        choices=CURRENCY_CHOICES, allow_blank=True, allow_null=True, default=dict)

    platform = serializers.ChoiceField(
        choices=PLATFORM_CHOICES, allow_blank=True, allow_null=True, default=dict)

    class Meta:
        model = Product
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=('name', 'platform'),
                message='Combination of name and platform already exists.'
            )
        ]

    # def validate_product_id(self, value):
    #     if Product.objects.filter(product_id=value).exists():
    #         raise serializers.ValidationError(
    #             'product id field must be unique.')
    #     return value


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
            payment = AndroidNotify.objects.filter(
                transaction_id=transaction_id)
            if payment.exists():
                return super().update(payment.first(), validated_data)
        return super().create(validated_data)


class GradePackSerializer(serializers.ModelSerializer):
    CATEGORY_CHOICES = [
        ('Nursery', 'Nursery'),
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
    ]

    LABEL_CHOICES = [
        ('Grade', 'Grade'),
        ('JSS', 'JSS'),
        ('KG', 'KG'),
        ('SSS', 'SSS'),
    ]

    RANGE_CHOICES = [
        ('1 - 3', '1 - 3'),
        ('4 - 6', '4 - 6'),
        ('7 - 9', '7 - 9'),
        ('10 - 12', '10 - 12'),
    ]

    label = serializers.ChoiceField(
        choices=LABEL_CHOICES, allow_blank=True, allow_null=True, default=dict)
    category = serializers.ChoiceField(
        choices=CATEGORY_CHOICES, allow_blank=True, allow_null=True, default=dict)
    range = serializers.ChoiceField(
        choices=RANGE_CHOICES, allow_blank=True, allow_null=True, default=dict)

    class Meta:
        model = GradePack
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=GradePack.objects.all(),
                fields=('label', 'range'),
                message='Combination of label and range already exists.'
            )
        ]
