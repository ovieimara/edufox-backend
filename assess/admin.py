from django.contrib import admin
from .models import Test, Assessment

# Register your models here.


class TestAdmin(admin.ModelAdmin):
    search_fields = ['subject__name', 'topic__title', 'lesson__title']
    list_display = ['pk', 'code', 'subject', 'question', 'options',
                    'valid_answers', 'grade', 'topic', 'lesson']

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
