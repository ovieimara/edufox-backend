import io
from abc import ABC, abstractmethod
from os import environ
from pathlib import Path
from google.cloud import secretmanager as secret_manager
import environ
from environ import Env
from storages.backends.gcloud import GoogleCloudStorage
from edufox.constants import platforms


class SecretRepoABC(ABC):
    env = Env(DEBUG=(bool, True), USE_CLOUD_BUILD=(bool, True))

    @abstractmethod
    def getEnvironmentVariables(self) -> tuple:
        pass


class GoogleCloudSecretRepo(SecretRepoABC):
    def __init__(self, settings_name: str, project_id: str) -> None:
        _client = secret_manager.SecretManagerServiceClient()
        _name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
        self.payload = _client.access_secret_version(
            name=_name).payload.data.decode("UTF-8")

    def getEnvironmentVariables(self) -> tuple:
        return self.env, environ.Env.read_env, io.StringIO(self.payload)
        # return self.env.read_env(io.StringIO(self.payload))


class LocalCredentialsRepo(SecretRepoABC):

    def getEnvironmentVariables(self) -> tuple:
        # env = Env()
        # environ.Env.read_env()
        # print('env: ', self.env())
        return self.env, environ.Env.read_env


class StorageRepoABC(ABC):
    @abstractmethod
    def getSignedUrl(self) -> str:
        pass


class GoogleCloudStorageRepo(StorageRepoABC):

    def __init__(self, path: str) -> None:

        self.path = path
        # BASE_DIR = Path(__file__).resolve().parent.parent
        # env_file = os.path.join(BASE_DIR, 'creds.json')
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env_file
        self.gcs_client = GoogleCloudStorage()

    def getSignedUrl(self) -> str:
        # Get the signed URL for the requested resource
        # file_path = f"{self.path}/{self.platforms.get(platform)}"
        return self.gcs_client.url(self.path)


class PlatformStream(ABC):
    def __init__(self, path) -> None:
        self.path = path

    @abstractmethod
    def getPlatformStream(self):
        ''' returns dash or hls stream depending on which platform is requesting(IOS/Android/Web)'''


class DashStream(PlatformStream):
    def getPlatformStream(self) -> StorageRepoABC:
        return GoogleCloudStorageRepo(f"{self.path}/manifest.mpd")


class HLSStream(PlatformStream):
    def getPlatformStream(self) -> StorageRepoABC:
        return GoogleCloudStorageRepo(f"{self.path}/playlist.m3u8")
