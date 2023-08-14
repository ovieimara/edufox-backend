import decimal
from enum import Enum
import logging
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from course.models import Grade
from subscribe.models import Discount

# Create your models here.


class Earn(models.Model):
    user = models.OneToOneField(
        User, related_name='user_earn', null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00)


class Referral(models.Model):
    # the owner of referral code(my_referral_code)
    user = models.OneToOneField(
        User, related_name='user_referral', null=True, blank=True, on_delete=models.CASCADE)
    code = models.CharField(
        db_index=True, max_length=15, null=True, blank=True, default="")
    status = models.CharField(
        max_length=255, null=True, blank=True, default='')
    # amount earned by the owner of the referral
    earn = models.ForeignKey(
        Earn, related_name='referral_earning', null=True, blank=True, default=1, on_delete=models.SET_NULL)
    discount = models.ForeignKey(
        Discount, related_name='discount_referral', null=True, default=1, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}-{self.code}"

    # def generate_code(self):
    #     arr = self.user.email.split('@')
    #     email = arr[0] if len(arr) >= 0 else ''
    #     return f"{self.user.first_name or self.user.first_name or email}{self.user.phone_number[-1:-5]}"
    @property
    def get_earning(self) -> float:
        return f"{self.referral_student.count() * self.earn.amount :.2f}" if self else 0.00


class Student(models.Model):
    # first_name = models.CharField(
    #     max_length=255, null=True, blank=True, default='')
    # last_name = models.CharField(
    #     max_length=255, null=True, blank=True, default='')
    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE)
    phone_number = models.CharField(db_index=True, max_length=15, default='')
    grade = models.ForeignKey(
        Grade, related_name='student_grade', null=True, on_delete=models.SET_NULL)
    # grade = models.CharField(db_index=True, max_length=255, null = True, blank=False)
    age = models.SmallIntegerField(db_index=True, null=True, default=0)
    dob = models.DateField(null=True, blank=True, db_index=True)
    gender = models.CharField(
        db_index=True, max_length=255, blank=True, null=True, default='')
    image_url = models.URLField(null=True, blank=True, default='')
    referral = models.ForeignKey(
        Referral, related_name='referral_student', null=True, on_delete=models.SET_NULL)
    name_institution = models.CharField(
        max_length=255, null=True, blank=True, default='')
    my_referral = models.CharField(
        db_index=True, max_length=255, blank=True, null=True, default='')
    registration_date = models.DateTimeField(
        db_index=True, null=True, auto_now_add=True)
    last_updated = models.DateTimeField(
        db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}"

    @property
    def my_referral_code(self) -> str:
        arr = self.user.email.split('@')
        email = arr[0] if len(arr) >= 0 else ''
        return f"{self.user.first_name or self.user.last_name or email}{self.user.username[:-4:-1]}"

    @property
    def earning(self) -> float:
        earned_amount_per_referral = 1
        count = 0
        try:
            count = Student.objects.filter(
                referral__code=self.my_referral_code).count()
            earn_instance = Earn.objects.get(user=self.user)
            if earn_instance:
                return f"{earn_instance.amount * count: .2f}"
        except Student.DoesNotExist as ex:
            logging.error(f"Referral: {ex}")
        except Earn.DoesNotExist as ex:
            logging.error(f"Earn: {ex}")

        return f"{count * earned_amount_per_referral: .2f}"


class Country(models.Model):
    code = models.CharField(db_index=True, max_length=15,
                            unique=True, null=True, blank=True, default="")
    name = models.CharField(db_index=True, unique=True,
                            max_length=100, null=True, blank=True, default="")
    icon = models.URLField(null=True, blank=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class TempStudent(models.Model):
    # student_id = models.CharField(db_index=True, max_length=15, null = True, blank=True, default="")
    username = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default="")
    first_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default="")
    last_name = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default="")
    email = models.EmailField()
    password = models.CharField(max_length=255)
    phone_number = models.CharField(
        db_index=True, max_length=15, null=True, default="")
    grade = models.ForeignKey(
        Grade, related_name='temp_student_grade', null=True, on_delete=models.SET_NULL)
    # grade = models.CharField(db_index=True, max_length=255, null = True, blank=False)
    age = models.SmallIntegerField(db_index=True, null=True)
    gender = models.CharField(
        db_index=True, max_length=255, null=True, blank=True, default='')
    image_url = models.URLField(null=True, blank=True, default='')
    name_institution = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(
        Country, related_name='countries', null=True, on_delete=models.SET_NULL)
    registration_date = models.DateTimeField(
        db_index=True, null=True, auto_now_add=True)
    last_updated = models.DateTimeField(
        db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
