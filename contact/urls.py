from django.urls import path, include
from .views import ListCreateAPIContact, ListCreateAPIContactForm

app_name = 'contact'

urlpatterns = [
    path('', ListCreateAPIContact.as_view(), name='contact-list'),
    path('form', ListCreateAPIContactForm.as_view(), name='contact-form-list'),

]
