from django.contrib import admin
from banner.models import Banner

# Register your models here.


class BannerAdmin(admin.ModelAdmin):
    # Add the fields you want to search
    search_fields = ['label', 'name', 'url']

    list_display = ['pk', 'is_active', 'label', 'name', 'url',
                    'dimensions', 'text', 'created', 'updated']


admin.site.register(Banner, BannerAdmin)
