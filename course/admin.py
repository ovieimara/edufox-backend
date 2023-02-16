from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from .models import Grade, Subject, Lecturer

# Register your models here.

class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'created', 'updated']

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'credits', 'created', 'updated']

class LecturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'get_subjects']

    def get_subjects(self, obj):
        return "\n".join([str(s) for s in obj.subject.all()])

admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lecturer, LecturerAdmin)