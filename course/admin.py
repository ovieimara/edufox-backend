from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from .models import Grade, Subject, Lecturer, Rate, Topic, Video, Comment, Interaction, Lesson
# from assess.models import  Test, Assessment

# Register your models here.


class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'created', 'updated']


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name',
                    'description', 'credits', 'created', 'updated']


class LecturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'get_subjects']

    def get_subjects(self, obj):
        return "\n".join([str(s) for s in obj.subject.all()])


class RateAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'video', 'created', 'updated']


class VideoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'video_id', 'title', 'description', 'duration', 'resolution',
                    'thumbnail', 'subject', 'get_grades', 'get_lesson', 'topic', 'url', 'url2', 'tags']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])

    def get_lesson(self, obj):
        return obj.lesson.num


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'video', 'created', 'updated']

# class InteractionTypeAdmin(admin.ModelAdmin):
#     list_display = ['code', 'name']


class InteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'video',
                    'created', 'updated']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'num', 'title', 'topic', 'subject', 'get_grades']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])


class TopicAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'title', 'subject', 'get_grades']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])


admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
# admin.site.register(InteractionType, InteractionTypeAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Topic, TopicAdmin)
