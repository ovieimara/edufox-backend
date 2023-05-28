from django.urls import path, include
from .views import (FetchSubscribe, ListCreateUpdateAPIDiscount, ListCreateUpdateAPISubscribe,
                    ListCreateUpdateAPIPlan, ListCreateUpdateAPIBillingProduct, VerifyPurchase,
                    AppStoreNotificationHandler, PlayStoreNotificationHandler, ListCreateUpdateAPIGradePack)
from djoser.views import UserViewSet

app_name = 'subscribe'

urlpatterns = [
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.authtoken')),
    path('subscribe', ListCreateUpdateAPISubscribe.as_view(), name='subscribe-list'),
    path('subscribe/<pk>', ListCreateUpdateAPISubscribe.as_view(),
         name='subscribe-detail'),
    path('fetch_subscribe', FetchSubscribe.as_view(),
         name='fetch-subscribe-detail'),
    path('discounts', ListCreateUpdateAPIDiscount.as_view(), name='discounts-list'),
    path('discounts/<pk>', ListCreateUpdateAPIDiscount.as_view(),
         name='discount-details'),
    path('plans', ListCreateUpdateAPIPlan.as_view(), name='plans-list'),
    path('plans/<pk>', ListCreateUpdateAPIPlan.as_view(), name='plan-detail'),
    path('products', ListCreateUpdateAPIBillingProduct.as_view(),
         name='products-list'),
    path('products/<pk>', ListCreateUpdateAPIBillingProduct.as_view(),
         name='product-detail'),
    path('grade_packs', ListCreateUpdateAPIGradePack.as_view(),
         name='grade-pack-list'),
    path('grade_packs/<pk>', ListCreateUpdateAPIGradePack.as_view(),
         name='grade-pack-detail'),
    path('verifyReceipt', VerifyPurchase, name='verifyReceipt-list'),
    path('appstorenotify', AppStoreNotificationHandler,
         name='appstorenotify-list'),
    path('playstorenotify', PlayStoreNotificationHandler,
         name='playstorenotify-list'),


]
