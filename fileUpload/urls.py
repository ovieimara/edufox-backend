# urls.py

from django.urls import path
from .views import FileUploadView

app_name = 'fileUpload'
urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    # Add other URLs as needed
]
