from django.contrib import admin
from .models import Subscribe, AndroidNotify

# Register your models here.

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'payment_method']


class AndroidNotifyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_id', 'purchase_token', 'expires_date', 'purchase_date', 'start_time', 'subscription_Id', 'purchaseState', 'acknowledgementState', 'consumptionState', 'paymentState', 'country_code', 'regionCode', 'amount', 'currency']

admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(AndroidNotify, AndroidNotifyAdmin)