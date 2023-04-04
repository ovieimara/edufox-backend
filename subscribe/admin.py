from django.contrib import admin
from .models import Subscribe

# Register your models here.

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'payment_method', 'grade']

admin.site.register(Subscribe, SubscribeAdmin)