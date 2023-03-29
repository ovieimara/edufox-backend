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
    discount = models.ForeignKey(Discount, related_name='discounts', null=True, default=1, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"{self.name}-{self.amount}"
    
class Product(models.Model):
    name = models.CharField(max_length=255, null=True, default='')
    product_id = models.CharField(max_length=255, null=True, default='')
    platform = models.CharField(max_length=255, null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class InAppPayment(models.Model):
    name = models.CharField(max_length=255, null=True, default='')
    environment = models.CharField(max_length=255, null=True, default='')
    original_transaction_id = models.CharField(max_length=255, null=True, default='')
    transaction_id = models.CharField(max_length=255, null=True, default='')
    posix_date_time = models.CharField(max_length=255, null=True, default='')
    expires_date = models.CharField(max_length=255, null=True, default='')
    # product_id = models.CharField(max_length=255, null=True, default='')
    product = models.ForeignKey(Product, related_name='products', null=True, default=1, on_delete=models.SET_NULL)
    original_transaction_id2 = models.CharField(max_length=255, null=True, default='')
    auto_renew_status = models.CharField(max_length=255, null=True, default='')
    expiration_intent = models.CharField(max_length=255, null=True, default='')
    in_app_ownership_type = models.CharField(max_length=255, null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
    
class Subscribe(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions_user', null=True, default=1,
    on_delete=models.SET_NULL)
    plan = models.ForeignKey(Plan, related_name='plans', null=True, default=1, on_delete=models.SET_NULL)
    payment = models.ForeignKey(InAppPayment, related_name='gateways', null=True, on_delete=models.SET_NULL)
    grade = models.ForeignKey(Grade, related_name='subscription_grade', null=True, default=1, on_delete=models.SET_NULL)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    # expiry_date = models.DateTimeField(db_index=True, null=True, default=datetime.now)

    @property
    def expiry_date(self):
        return self.created + timedelta(days=self.plan.duration)

    def is_valid(self, now):
        expiry_date = self.expiry_date
        # isGrade = self.grade == grade
        if expiry_date and expiry_date > now:
            return True

        return False


