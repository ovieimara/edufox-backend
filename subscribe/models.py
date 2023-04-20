from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from course.models import Grade 
from django.utils import timezone

# Create your models here.
class Discount(models.Model):
    name = models.CharField(max_length=255, null=True, default='')
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    symbol = models.CharField(max_length=127, null=True, default=True)

    def __str__(self) -> str:
        return self.name

class Plan(models.Model):
    name = models.CharField(max_length=100, null=True, default='')
    amount = models.IntegerField()
    currency = models.CharField(max_length=15, null=True, default='=N=')
    description = models.TextField(null=True, default='')
    duration = models.SmallIntegerField(default=0)
    discount = models.ForeignKey(Discount, related_name='discount_plans', null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.name}-{self.amount}"
    
class Product(models.Model):
    name = models.CharField(max_length=255, null=True,  blank=True, unique=True, default='')
    product_id = models.CharField(max_length=255, null=True, unique=True, blank=True, default='')
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=15, null=True,  blank=True,default='=N=')
    duration = models.SmallIntegerField(null=True, blank=True, default=0)
    discount = models.ForeignKey(Discount, related_name='discount_products', null=True, on_delete=models.SET_NULL)
    platform = models.CharField(max_length=255, null=True, blank=True, default='')
    description = models.TextField(null=True, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class InAppPayment(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default='')
    environment = models.CharField(max_length=255, null=True, blank=True,default='')
    original_transaction_id = models.CharField(max_length=255, null=True, blank=True, default='')
    transaction_id = models.CharField(max_length=255, null=True, blank=True,default='')
    # expires_date = models.CharField(max_length=255, null=True, blank=True, default='')
    expires_date = models.DateTimeField(null=True, blank=True, default=datetime.now)
    original_purchase_date = models.DateTimeField(null=True, blank=True, default=datetime.now)
    product = models.ForeignKey(Product, related_name='products', null=True, blank=True, on_delete=models.SET_NULL)
    auto_renew_status = models.CharField(max_length=255, null=True, blank=True, default='')
    expiration_intent = models.CharField(max_length=255, null=True, blank=True, default='')
    in_app_ownership_type = models.CharField(max_length=255, null=True, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
class Subscribe(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions_user', null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, related_name='product_subscribers', null=True, on_delete=models.SET_NULL)
    # plan = models.ForeignKey(Plan, related_query_name='plans', on_delete=models.SET_NULL, null=True, blank=True)
    payment_method= models.ForeignKey(InAppPayment, related_name='payment_method_subscriptions', null=True, on_delete=models.SET_NULL)
    grade = models.ForeignKey(Grade, related_name='subscription_grade', null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    @property
    def expiry_date(self):
        # print(self.created , self.created + timedelta(days=self.product.duration))
        return self.created + timedelta(days=self.product.duration)

    def is_valid(self, now):
        expiry_date = self.expiry_date
        # isGrade = self.grade == grade
        if expiry_date and expiry_date > now:
            return True

        return False
    
class AppleNotify(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default='Apple In-App')
    environment = models.CharField(max_length=255, null=True, blank=True,default='')
    original_transaction_id = models.CharField(max_length=255, null=True, blank=True, default='')
    transaction_id = models.CharField(max_length=255, null=True, blank=True,default='')
    expires_date = models.DateTimeField(db_index=True, null=True, default=datetime.now)
    original_purchase_date = models.DateTimeField(null=True, blank=True, default=datetime.now)
    product_id = models.CharField(max_length=255, null=True, blank=True, default='')
    auto_renew_status = models.CharField(max_length=255, null=True, blank=True, default='')
    expiration_intent = models.CharField(max_length=255, null=True, blank=True, default='')
    in_app_ownership_type = models.CharField(max_length=255, null=True, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class AndroidNotify(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, default='Android In-App')
    transaction_id = models.CharField(max_length=255, null=True, blank=True, default='')
    purchase_token = models.CharField(max_length=255, null=True, blank=True, default='')
    expires_date = models.DateTimeField(db_index=True, null=True, default=datetime.now)
    purchase_date = models.DateTimeField(null=True, blank=True, default=datetime.now)
    start_time = models.DateTimeField(null=True, blank=True, default=datetime.now)
    subscription_Id = models.CharField(max_length=255, null=True, blank=True, default='')
    purchaseState = models.SmallIntegerField(default=1)
    acknowledgementState = models.SmallIntegerField(default=0)
    consumptionState = models.SmallIntegerField(default=0)
    paymentState = models.SmallIntegerField(default=0)
    country_code = models.CharField(max_length=255, null=True, blank=True, default='')
    regionCode = models.CharField(max_length=255, null=True, blank=True, default='')
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, null=True, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)