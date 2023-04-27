from django.contrib import admin
from .models import Subscribe, AndroidNotify, InAppPayment

# Register your models here.

class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'payment_method', 'created']


class AndroidNotifyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_id', 'purchase_token', 'expires_date', 'purchase_date', 'start_time', 'subscription_Id', 'purchaseState', 'acknowledgementState', 'consumptionState', 'paymentState', 'country_code', 'regionCode', 'amount', 'currency']

class InAppPaymentAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_id', 'original_transaction_id', 'transaction_id', 'expires_date', 'original_purchase_date', 'created']

admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(AndroidNotify, AndroidNotifyAdmin)
admin.site.register(InAppPayment, InAppPaymentAdmin)