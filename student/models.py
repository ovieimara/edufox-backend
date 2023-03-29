from django.db import models
from django.contrib.auth.models import User, Group, Permission
from course.models import Grade

# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    phone_number = models.CharField(db_index=True, max_length=15, default='')
    grade = models.ForeignKey(Grade, related_name='student_grade', null=True, on_delete=models.SET_NULL)
    # grade = models.CharField(db_index=True, max_length=255, null = True, blank=False)
    age = models.SmallIntegerField(db_index=True, null=True, default=0)
    gender = models.CharField(db_index=True, max_length=255, blank=True, null=True, default='')
    image_url = models.URLField(null=True, blank=True, default='')
    name_institution = models.CharField(max_length=255, null = True, blank=True, default='')
    registration_date = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username}"

class Country(models.Model):
    code = models.CharField(db_index=True, max_length=15, unique=True, null=True, blank=True, default="")
    name = models.CharField(db_index=True, unique=True, max_length=100, null=True, blank=True, default="")
    icon = models.URLField(null=True, blank=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"

class TempStudent(models.Model):
    # student_id = models.CharField(db_index=True, max_length=15, null = True, blank=True, default="")
    username = models.CharField(db_index=True, max_length=255, null=True, blank=True, default="")
    first_name  = models.CharField(db_index=True, max_length=255, null = True, blank=True, default="")
    last_name  = models.CharField(db_index=True, max_length=255, null = True, blank=True, default="")
    email = models.EmailField()
    password = models.CharField(max_length=255)
    phone_number = models.CharField(db_index=True, max_length=15, null = True, default="")
    grade = models.ForeignKey(Grade, related_name='temp_student_grade', null=True, on_delete=models.SET_NULL)
    # grade = models.CharField(db_index=True, max_length=255, null = True, blank=False)
    age = models.SmallIntegerField(db_index=True, null=True)
    gender = models.CharField(db_index=True, max_length=255, null=True, blank=True, default='')
    image_url = models.URLField(null = True, blank=True, default='')
    name_institution = models.CharField(max_length=255, null = True, blank=True)
    country = models.ForeignKey(Country, related_name='countries', null=True, on_delete=models.SET_NULL)
    registration_date = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    last_updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


