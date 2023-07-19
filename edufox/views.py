import copy
import io
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.cache import cache
import logging as log
from google.cloud import logging
from abc import ABC, abstractmethod
from google.cloud import secretmanager
import os
from environ import Env


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


class SecretRepoABC(ABC):
    @abstractmethod
    def getEnvVariables():
        pass


class GoogleCloudSecretRepo(SecretRepoABC):
    def __init__(self, settings_name: str, project_id: str) -> None:
        self._client = secretmanager.SecretManagerServiceClient()
        self._name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
        self.payload = self._client.access_secret_version(
            name=self._name).payload.data.decode("UTF-8")

    def getEnvironmentVariables(self, env: Env):
        return env.read_env(io.StringIO(self.payload))


class LocalCredentialsRepo(SecretRepoABC):

    def getEnvVariables(self, env: Env):
        env = Env()
        return env.read_env()
