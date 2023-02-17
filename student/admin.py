from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from .models import Student, TempStudent

# Register your models here.

# class UserAdminForm(forms.ModelForm):
#     GENDER_CHOICES =(
#     ("Male", "Male"),
#     ("Female", "Female"),
# )
#     first_name = forms.CharField()
#     last_name = forms.CharField()
#     username = forms.CharField()
#     email = forms.EmailField()
#     # age = forms.IntegerField(max_value=150, min_value=1)
#     # gender = forms.ChoiceField(choices=GENDER_CHOICES)
#     # image_url = forms.CharField(max_length=1024)
#     # name_institution = forms.CharField(max_length=255)

#     class Meta:
#         model = Student
#         fields = ['student_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'grade',  'age', 'gender', 'image_url', 'name_institution']

class TempStudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'grade', 'age', 'gender', 'image_url']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'grade', 'age', 'gender', 'image_url']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'grade', 'age', 'gender', 'image_url']


# admin.site.unregister(User)
# admin.site.register(Student)
admin.site.register(Student, StudentAdmin)
admin.site.register(TempStudent, TempStudentAdmin)
