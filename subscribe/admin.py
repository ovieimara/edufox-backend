from django.contrib import admin
from .models import Subscribe, AndroidNotify, InAppPayment, Product

# Register your models here.


class SubscribeAdmin(admin.ModelAdmin):
    search_fields = ['user', 'created']
    list_display = ['pk', 'user', 'product', 'payment_method',
                    'grade', 'created', 'updated']

    # def get_grades(self, obj):
    #     return "\n".join([str(s) for s in obj.grade])


class AndroidNotifyAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_id', 'purchase_token', 'expires_date', 'purchase_date', 'start_time', 'subscription_Id', 'purchaseState',
                    'acknowledgementState', 'consumptionState', 'paymentState', 'country_code', 'regionCode', 'amount', 'currency', 'created', 'updated']


class InAppPaymentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'name', 'product_id', 'original_transaction_id', 'transaction_id',
                    'expires_date', 'original_purchase_date', 'created', 'updated']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_id', 'amount',
                    'currency', 'duration', 'platform', 'description',  'created', 'updated']


admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(AndroidNotify, AndroidNotifyAdmin)
admin.site.register(InAppPayment, InAppPaymentAdmin)
admin.site.register(Product, ProductAdmin)
