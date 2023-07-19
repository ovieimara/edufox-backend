from abc import abstractmethod, ABC
import google.auth
from google.cloud import secretmanager
from urllib.parse import urlparse
from google.oauth2 import service_account
import environ


# class


# env = environ.Env(DEBUG=(bool, True), USE_CLOUD_BUILD=(bool, True))

# PROJECT_ID = "edufox-services"
# client = secretmanager.SecretManagerServiceClient()

# settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
# name = f"projects/{PROJECT_ID}/secrets/{settings_name}/versions/latest"
# payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
# env.read_env(io.StringIO(payload))
