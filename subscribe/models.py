from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from course.models import Grade 

# Create your models here.
class Discount(models.Model):
    name = models.CharField(max_length=255, null=True, default='')
    value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    symbol = models.CharField(max_length=127, null=True, default=True)

class Plan(models.Model):
    amount = models.SmallIntegerField()
    currency = models.CharField(max_length=15, null=True, default='=N=')
    description = models.TextField(null=True, default='')
    duration = models.SmallIntegerField(default=0)
    discount = models.ForeignKey(Discount, related_name='discounts', on_delete=models.CASCADE)

class Subscribe(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions_user', null=True, 
    on_delete=models.SET_NULL)
    plan = models.ForeignKey(Plan, related_name='plans', null=True, on_delete=models.SET_NULL)
    grade = models.ForeignKey(Grade, related_name='subscription_grade', null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    

    def get_expiry_date(self):
        #created + plan.duration
        return self.created.date() + timedelta(days=self.plan__duration)

    def is_valid(self, now):
        expiry_date = self.get_expiry_date()
        # isGrade = self.grade == grade
        if expiry_date and expiry_date > now:
            return True

        return False

