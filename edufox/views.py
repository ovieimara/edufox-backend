import copy
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.cache import cache


@api_view(['GET'])
# @permission_classes([AllowAny])
def PrivacyPolicy(request, *args, **kwargs):
    return render(request, 'privacy.html')


def update_user_data():
    # Update user-specific data in the database

    # Invalidate cache for the specific user
    cache.clear()
