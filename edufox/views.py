import copy
from django.shortcuts import render
from rest_framework.decorators import api_view



@api_view(['GET'])
# @permission_classes([AllowAny])
def PrivacyPolicy(request, *args, **kwargs):
    return render(request, 'privacy.html')
