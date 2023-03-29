from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from .models import Grade, Subject, Lecturer, Rate, Video, Comment, Interaction
# from assess.models import  Test, Assessment

# Register your models here.

class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'created', 'updated']

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'credits', 'created', 'updated']

class LecturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'get_subjects']

    def get_subjects(self, obj):
        return "\n".join([str(s) for s in obj.subject.all()])

class RateAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'video', 'created', 'updated']

class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'duration', 'resolution', 
    'thumbnail', 'subject', 'get_grades', 'get_lesson', 'topic']
    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])
    
    def get_lesson(self, obj):
        return obj.lesson.num

class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'video', 'created', 'updated']

# class InteractionTypeAdmin(admin.ModelAdmin):
#     list_display = ['code', 'name']

class InteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'video', 'duration', 'created', 'updated']

# class TestAdmin(admin.ModelAdmin):
#     list_display = ['code', 'subject', 'question', 'options', 'grade', 'difficulty_level']

# class AssessmentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'get_tests', 'answer', 'status']
#     def get_tests(self, obj):
#         return "\n".join([str(s) for s in obj.test.all()])


admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(InteractionType, InteractionTypeAdmin)
admin.site.register(Interaction, InteractionAdmin)
# admin.site.register(Test, TestAdmin)
# admin.site.register(Assessment, AssessmentAdmin)