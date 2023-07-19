from django.urls import path, include
from .views import ListCreateAPIContact, ListCreateAPIContactForm

app_name = 'contact'

urlpatterns = [
    path('', ListCreateAPIContact.as_view(), name='grades-list'),
    path('form', ListCreateAPIContactForm.as_view(), name='grades-list'),

]
