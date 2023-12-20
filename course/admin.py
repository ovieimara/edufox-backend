from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from .models import Grade, SearchQuery, Subject, Lecturer, Rate, Thumbnail, Topic, Video, Comment, Interaction, Lesson
# from assess.models import  Test, Assessment

# Register your models here.


class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'description', 'created', 'updated']


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'num', 'code', 'name',
                    'description', 'is_active', 'thumbnail', 'credits', 'created', 'updated']


class LecturerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'get_subjects']

    def get_subjects(self, obj):
        return "\n".join([str(s) for s in obj.subject.all()])


class RateAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'video', 'created', 'updated']


class VideoAdmin(admin.ModelAdmin):
    search_fields = ['video_id', 'title',
                     'subject__name', 'lesson__title', 'topic__title', 'grade__name']
    list_display = ['pk', 'video_id', 'title', 'description', 'duration', 'resolution',
                    'thumbnail', 'subject', 'get_grades', 'get_lesson', 'topic', 'url', 'url2', 'tags', 'created', 'updated']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])

    def get_lesson(self, obj):
        if obj:
            return obj.lesson.num if obj.lesson else ''
        return ''


class ThumbnailAdmin(admin.ModelAdmin):
    search_fields = ['subject__name', 'image_type']
    list_display = ['pk', 'subject', 'url', 'image_type', 'created', 'updated']

    # def get_urls(self, obj):
    #     return "\n".join([str(obj.url.all)])


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'video', 'created', 'updated']

# class InteractionTypeAdmin(admin.ModelAdmin):
#     list_display = ['code', 'name']


class InteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'video',
                    'created', 'updated']


class LessonAdmin(admin.ModelAdmin):
    # Add the fields you want to search
    search_fields = ['title', 'subject__name',
                     'topic__title', 'grade__name', 'is_active']

    list_display = ['pk', 'num', 'title', 'topic',
                    'subject', 'get_grades', 'is_active', 'created', 'updated']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])


class TopicAdmin(admin.ModelAdmin):
    search_fields = ['title', 'subject__name', 'grade__name']
    list_display = ['pk', 'chapter', 'title',
                    'subject', 'get_grades', 'created']

    def get_grades(self, obj):
        return "\n".join([str(s) for s in obj.grade.all()])


class SearchQueryAdmin(admin.ModelAdmin):
    search_fields = ['query']
    list_display = ['pk', 'query', 'created', 'updated']


admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SearchQuery, SearchQueryAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
