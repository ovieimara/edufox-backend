from django.contrib import admin
from .models import Test, Assessment

# Register your models here.


class TestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'code', 'subject', 'question', 'options',
                    'valid_answers', 'grade', 'topic', 'lesson']

    # def get_levels(self, obj):
    #     return "\n".join([str(s) for s in obj.level.all() if s])


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_tests', 'answer']

    def get_tests(self, obj):
        return "\n".join([str(obj.test.question)])


admin.site.register(Test, TestAdmin)
admin.site.register(Assessment, AssessmentAdmin)
