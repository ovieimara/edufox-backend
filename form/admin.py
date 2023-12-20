from django.contrib import admin

from form.models import Waiter

# Register your models here.


class WaiterAdmin(admin.ModelAdmin):
    list_display = ['pk', 'first_name',
                    'last_name', 'email', 'created', 'updated']


admin.site.register(Waiter, WaiterAdmin)
