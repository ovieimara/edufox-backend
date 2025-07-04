"""edufox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
# from rest_framework.documentation import include_docs_urls
from student.views import CreateAPIUser, apiViewManager
from rest_framework_swagger.views import get_swagger_view
from .views import PrivacyPolicy, StandardEula

schema_view = get_swagger_view(title='EduFox API')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/auth/', include('student.urls')),
    path('api/auth', apiViewManager, name="api-view"),
    path('api/', include('version.urls')),
    re_path(r'^$', schema_view),
    path('privacy/', PrivacyPolicy),
    path('seula/', StandardEula),

]
