from datetime import datetime, timedelta
from functools import lru_cache
import io
from abc import ABC, abstractmethod
import logging
from os import environ
import os
from pathlib import Path
from google.cloud import secretmanager as secret_manager
from google.cloud import storage
import environ
from environ import Env
from storages.backends.gcloud import GoogleCloudStorage
from edufox.constants import platforms
import boto3
from botocore.config import Config
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import boto3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner


class SecretRepoABC(ABC):
    # env = Env(DEBUG=(bool, True), USE_CLOUD_BUILD=(bool, True))
    env: environ.Env = Env(DEBUG=(bool, True), USE_CLOUD_BUILD=(bool, True))

    @abstractmethod
    def getEnvironmentVariables(self) -> tuple:
        pass

    @abstractmethod
    def getParams(self):
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

    def getParams(self):
        return {
            "GS_BUCKET_NAME": 'edufox-bucket-2',
            "GS_PROJECT_ID": self.env("GOOGLE_CLOUD_PROJECT"),
            "DEFAULT_FILE_STORAGE": "storages.backends.gcloud.GoogleCloudStorage",
            "STATICFILES_STORAGE": "storages.backends.gcloud.GoogleCloudStorage",
            # GS_DEFAULT_ACL = "publicRead"
            "GS_AUTO_CREATE_BUCKET": True,
            "GS_QUERYSTRING_AUTH": True,
        }


class LocalCredentialsRepo(SecretRepoABC):

    def getEnvironmentVariables(self) -> tuple:
        return self.env, environ.Env.read_env

    def getParams(self):
        return {}


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


class GoogleCloudStorageRepo2(StorageRepoABC):
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_file = os.path.join(BASE_DIR, 'creds.json')

    def __init__(self, path: str, bucket_name: str, expiration: int = 3600 * 3) -> None:

        self.path = path
        self.bucket_name = bucket_name
        self.expiration = expiration
        self.gcs_client = storage.Client.from_service_account_json(
            self.env_file)

    def getSignedUrl(self):
        """Generate a signed URL to access a private object in a bucket."""
        # Initialize the GCS client with your credentials

        # Get the bucket
        bucket = self.gcs_client.get_bucket(self.bucket_name)

        # Get the blob (object) in the bucket
        blob = bucket.blob(self.path)

        # Set the expiration time for the signed URL
        expiration_time = timedelta(seconds=self.expiration)
        expiration_datetime = datetime.utcnow() + expiration_time

        # Generate the signed URL
        signed_url = blob.generate_signed_url(expiration=expiration_datetime)
        return signed_url


class AmazonSimpleStorageRepo(StorageRepoABC):

    def __init__(self, bucket_name: str, object_key: str, expiration_time: int) -> None:
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.expiration_time = expiration_time

    def getSignedUrl(self):
        # Create an S3 client
        s3_client = boto3.client('s3')

        # Generate a signed URL for the S3 object
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': self.object_key
            },
            ExpiresIn=self.expiration_time
        )

        return signed_url


class AmazonDynamoDBRepo():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('edufox-video-on-demand-stack')

    # def __init__(self) -> None:
    # self.partition_key_value = partition_key_value

    def getHlsUrl(self, partition_key_value: str = "") -> str:
        egressEndpoints = hls = ''
        try:
            response = self.table.get_item(
                Key={
                    'guid': partition_key_value
                }
            )
            item = response.get('Item')
            if item:
                egressEndpoints = item.get('egressEndpoints')

            if egressEndpoints:
                hls = egressEndpoints.get('HLS')

        except Exception as ex:
            logging.error(f"getSignedUrl: {ex}")

        print('HLSS: ', hls)
        return hls

    def getSignedUrlFromScan2(self, srcVideoTitle: str, subject: str) -> tuple[str, str]:
        print("getSignedUrlFromScan: ", f"{subject}/{srcVideoTitle}.mp4")
        egressEndpoints = hls = item = guid = ''
        try:
            response = self.table.scan(
                FilterExpression=Attr('srcVideo').eq(
                    f"{subject}/{srcVideoTitle}.mp4")
            )
            items = response.get('Items') if response else ''

            if items:
                item = items[0]

            if item:
                guid = item.get('guid')
                egressEndpoints = item.get('egressEndpoints')

            if egressEndpoints:
                hls = egressEndpoints.get('HLS')

                # return item.get('guid'), item.get('egressEndpoints').get('HLS')
            # else:
        except Exception as ex:
            logging.error(f"getSignedUrlFromScan: {ex}")
            # return '', ''
        print(guid, hls)
        return guid, hls

    def getSignedUrlFromQuery(self, srcVideoTitle: str, subject: str) -> tuple[str, str]:
        print("getSignedUrlFromScan: ", f"{subject}/{srcVideoTitle}.mp4")
        egressEndpoints = hls = item = guid = ''
        dynamodb = boto3.client('dynamodb')

        try:
            # response = self.table.scan(
            #     FilterExpression=Attr('srcVideo').eq(
            #         "basic_technology/REPRODUCTION.mp4")
            # )
            response = dynamodb.query(
                TableName="edufox-video-on-demand-stack",
                IndexName="srcVideo-index",
                KeyConditionExpression="srcVideo = :srcVideo ",
                ExpressionAttributeValues={
                    ':srcVideo': {'S': f"{subject}/{srcVideoTitle}.mp4"},
                }
            )
            items = response.get('Items', [])

            if items:
                item = items[0]

            if item:
                guid = item.get('guid')
                if guid:
                    guid = guid.get('S', '')

                egressEndpoints = item.get('egressEndpoints')

            if egressEndpoints:
                endpoints = egressEndpoints.get('M')
                if endpoints:
                    HLS = endpoints.get('HLS')
                    if HLS:
                        hls = HLS.get('S', '')

                # print("HLSURL: ", hls)
                # return item.get('guid'), item.get('egressEndpoints').get('HLS')
            # else:
        except Exception as ex:
            logging.error(f"getSignedUrlFromScan: {ex}")
            # return '', ''
        print('HLSURL: ', guid, hls)

        return guid, hls


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


class HLSWebStream(PlatformStream):
    def __init__(self, path: str, bucket_name: str, expiration: int = 3600) -> None:
        super().__init__(path)
        self.bucket_name = bucket_name
        self.expiration = expiration

    def getPlatformStream(self) -> StorageRepoABC:
        return GoogleCloudStorageRepo2(f"{self.path}/playlist.m3u8", self.bucket_name, self.expiration)


class AmazonHLSStream(PlatformStream):
    def getPlatformStream(self) -> StorageRepoABC:
        return AmazonSimpleStorageRepo(f"{self.path}/playlist.m3u8")


class AmazonDynamoDBHLSStream(PlatformStream):
    def __init__(self, hls_url: str, expiresIn: datetime) -> None:
        self.hls_url = hls_url
        self.expiresIn = expiresIn
        self.key_pair_id = env('KEY_PAIR_ID')

    def getPlatformStream(self) -> StorageRepoABC:
        return AWSSignedURLGenerator(self.hls_url, self.expiresIn, self.key_pair_id)


class AWSSignedURLGenerator(StorageRepoABC):
    # cloudfront_signer = boto3.client('cloudfront').generate_presigned_url
    # cloudfront_client = boto3.client('cloudfront')
    s3 = boto3.client('s3')
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_file = os.path.join(BASE_DIR, 'private_key.pem')
    private_key_path = "../private_key.pem"

    # def __init__(self) -> None:
    # self.cloudfront_distribution_domain = "https://d3sf15wolo885z.cloudfront.net"

    # self.distribution_domain = f"d3sf15wolo885z.cloudfront.net"

    def __init__(self, hls_url: str, expiresIn: datetime, key_pair_id: str) -> None:
        self.hls_url = hls_url
        self.expiresIn = expiresIn
        self.key_pair_id = key_pair_id

    def getSignedUrl(self):
        signed_url = ''
        distribution_domain, object_key = self.hls_url.split('.net')
        url = f"{distribution_domain}.net{object_key}"

        try:
            cloudfront_signer = CloudFrontSigner(
                self.key_pair_id, self.rsa_signer)
            # Create a signed url that will be valid until the specific expiry date
            # provided using a canned policy.
            if cloudfront_signer:
                signed_url = cloudfront_signer.generate_presigned_url(
                    url, date_less_than=self.expiresIn)

        except Exception as ex:
            logging.error(f"cloudfront_signer error: {ex}")

        # cloudfront_signed_url = f'{signed_url}'

        # print('cloudfront_signed_url: ', cloudfront_signed_url)

        return signed_url if signed_url else ''

    def rsa_signer(self, message):
        try:
            with open(self.env_file, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())
        except Exception as ex:
            logging.error(f"rsa_signer error: {ex}")
            return ''
