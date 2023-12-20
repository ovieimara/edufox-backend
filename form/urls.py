# urls.py

from django.urls import path
from .views import ListCreateUpdateAPIWaiter

app_name = 'form'
urlpatterns = [
    path('waitlist', ListCreateUpdateAPIWaiter.as_view(), name='waitlist-list'),
    # Add other URLs as needed
]
