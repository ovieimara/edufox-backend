from django.contrib import admin

from contact.models import Contact, ContactForm

# Register your models here.


class ContactFormAdmin(admin.ModelAdmin):
    search_fields = ['phone_number', 'email', 'message']
    list_display = ['pk', 'phone_number',
                    'message', 'created', 'updated']


class ContactAdmin(admin.ModelAdmin):
    search_fields = ['phone_number', 'email']
    list_display = ['pk', 'phone_number', 'email', 'created', 'updated']


admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactForm, ContactFormAdmin)
