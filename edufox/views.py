import copy
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.cache import cache
import logging as log
from google.cloud import logging


@api_view(['GET'])
# @permission_classes([AllowAny])
def PrivacyPolicy(request, *args, **kwargs):
    return render(request, 'privacy.html')


def update_user_data():
    # Update user-specific data in the database

    # Invalidate cache for the specific user
    cache.clear()


def printOutLogs(tag='', param=''):
    logging_client = logging.Client()
    logging_client.get_default_handler()
    logging_client.setup_logging()
    log.info(f"Some log here: {tag} : {param}")
