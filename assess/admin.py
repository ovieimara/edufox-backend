from django.contrib import admin

from course.models import Lesson, Topic
from .models import Test, Assessment

# Register your models here.


class TestAdmin(admin.ModelAdmin):
    search_fields = ['question', 'valid_answers', 'options', 'subject__name',
                     'topic__title', 'lesson__title', 'grade__name']
    list_display = ['pk', 'code', 'subject', 'question', 'options',
                    'valid_answers', 'grade', 'topic', 'lesson']

    def get_subject(self, obj):
        return obj.subject.name

    def get_lesson(self, obj):
        return obj.lesson.title

    def get_topic(self, obj):
        return obj.topic.title

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'topic':
            kwargs['queryset'] = Topic.objects.order_by(
                'title')  # Sort topics by title descending
        elif db_field.name == 'lesson':
            kwargs['queryset'] = Lesson.objects.order_by('title')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # def get_levels(self, obj):
    #     return "\n".join([str(s) for s in obj.level.all() if s])


class AssessmentAdmin(admin.ModelAdmin):
    search_fields = ['user']
    list_display = ['user', 'get_tests',
                    'answer', 'created', 'updated']

    def get_tests(self, obj):
        return "\n".join([str(obj.test.question)])


admin.site.register(Test, TestAdmin)
admin.site.register(Assessment, AssessmentAdmin)
