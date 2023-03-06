# from django.contrib import admin
# from .models import Test, Assessment

# # Register your models here.

# class TestAdmin(admin.ModelAdmin):
#     list_display = ['code', 'subject', 'question', 'options', 'grade', 'get_levels', 'topic', 'lesson']

#     def get_levels(self, obj):
#         return "\n".join([str(s) for s in obj.level.all()])

# class AssessmentAdmin(admin.ModelAdmin):
#     list_display = ['user', 'get_tests', 'answer']
#     def get_tests(self, obj):
#         return "\n".join([str(obj.test.question)])
    
# admin.site.register(Test, TestAdmin)
# admin.site.register(Assessment, AssessmentAdmin)
