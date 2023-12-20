from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
import io
from abc import ABC, abstractmethod
import logging
from os import environ
import os
from pathlib import Path
from typing import List
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
import concurrent.futures

from django.core.cache import caches, cache


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
        # Set the expiration time for the signed URL
        expiration_time = timedelta(seconds=expiration)
        expiration_datetime = datetime.utcnow() + expiration_time
        self.path = path
        self.bucket_name = bucket_name
        self.expiration = expiration_datetime
        self.gcs_client = storage.Client.from_service_account_json(
            self.env_file)

    def getSignedUrl(self):
        """Generate a signed URL to access a private object in a bucket."""
        # Initialize the GCS client with your credentials

        # Get the bucket
        bucket = self.gcs_client.get_bucket(self.bucket_name)

        # Get the blob (object) in the bucket
        blob = bucket.blob(self.path)

        # Generate the signed URL
        signed_url = blob.generate_signed_url(expiration=self.expiration)
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


# @dataclass(slots=False)
class AmazonDynamoDBRepo():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('edufox-video-on-demand-stack')

    # def __init__(self) -> None:
    # self.partition_key_value = partition_key_value
    @lru_cache
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

        # print('HLSS: ', hls)
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
        # print("getSignedUrlFromScan: ", f"{subject}/{srcVideoTitle}.mp4")
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
        # print('HLSURL: ', guid, hls)

        return guid, hls


@dataclass
class AmazonDynamoDB():
    # Initialize DynamoDB client
    dynamodb: boto3.client = boto3.client('dynamodb', region_name='us-east-1')

    # DynamoDB table name
    table_name: str = "edufox-video-on-demand-stack"

    def update_item_by_guid(self, updated_data: dict = dict):
        s = ''
        try:
            response = self.dynamodb.update_item(
                TableName=self.table_name,
                Key={
                    'guid': {'S': updated_data.get('partition_key_value')}
                },
                # UpdateExpression='SET Attribute1 = :val1, Attribute2 = :val2',  # Update the necessary attributes
                UpdateExpression='SET srcVideo = :val',  # Update the necessary attributes

                ExpressionAttributeValues={
                    # Replace with the new values for your attributes
                    ':val': {'S': f"{updated_data.get('subject_code')}/{updated_data.get('title')}"},
                    # ':val2': {'S': updated_data['Attribute2']}
                },
                ReturnValues='UPDATED_NEW'
            )
            attributes = response.get('Attributes')

            if attributes:
                srcVideo = attributes.get('srcVideo')

            if srcVideo:
                s = srcVideo.get('S')

            # logging.info('Item updated successfully:', response)

            return s if s else ''

        except Exception as e:
            logging.error('Error updating item:', str(e))


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
    __slots__ = 'hls_url', 'expiresIn', 'key_pair_id'

    def __init__(self, hls_url: str, expiresIn: datetime) -> None:
        self.hls_url = hls_url
        self.expiresIn = expiresIn
        self.key_pair_id = os.environ.get('KEY_PAIR_ID')

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
            # with open(self.env_file, 'rb') as key_file:
            #     private_key = serialization.load_pem_private_key(
            #         key_file.read(),
            #         password=None,
            #         backend=default_backend()
            #     )
            private_key = readPrivateKeyFile(self.env_file)
            return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())
        except Exception as ex:
            logging.error(f"rsa_signer error: {ex}")
            return ''


@lru_cache
def readPrivateKeyFile(env_file: str):
    # print('RSA SIGNERSSS..............', env_file)
    private_key = ''
    try:
        with open(env_file, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
    except Exception as ex:
        logging.error(f"rsa_signer error: {ex}")

    return private_key
# class StorageDistributionConnector(ABC):

#     @abstractmethod
#     def list_images(self):
#         pass

#     @abstractmethod
#     def get_signed_urls(self):
#         pass


# @dataclass
# class AmazonS3CloudFront(StorageDistributionConnector):
#     # Initialize the S3 and CloudFront clients
#     s3_client: str = boto3.client('s3')
#     cloudfront_client = boto3.client('cloudfront')

#     # Set your S3 bucket and CloudFront distribution IDs
#     s3_bucket_name: str = os.environ.get('AWS_THUMBNAIL_BUCKET')
#     cloudfront_distribution_id: str = os.environ.get('AWS_DISTRIBUTION_ID')


class ImageStore(ABC):

    # Initialize the S3 and CloudFront clients
    # connector : StorageDistributionConnector = AmazonS3CloudFront()

    @abstractmethod
    def list_images_in_bucket(self):
        pass

    @abstractmethod
    def generate_signed_urls():
        pass


class AmazonImageStore(ImageStore):

    # Initialize the S3 and CloudFront clients
    s3_client: str = boto3.client('s3')
    cloudfront_client = boto3.client('cloudfront')

    def __init__(self, s3_bucket_name: str, cloudfront_distribution_id: str) -> None:
        # Set your S3 bucket and CloudFront distribution IDs
        self.s3_bucket_name: str = s3_bucket_name
        self.cloudfront_distribution_id: str = cloudfront_distribution_id
        self.s3_objects: list

    def list_images_in_bucket(self) -> None:
        self.s3_objects = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket_name)['Contents']

    @lru_cache
    def generate_signed_urls(self) -> list:
        # Generate signed URLs for each object
        signed_urls = []
        for s3_object in self.s3_objects:
            object_key = s3_object['Key']
            # print('object_key', object_key)
            # url = f'https://d348w3g6ndshex.cloudfront.net/{object_key}'
            signed_url = self.getSignedUrl(
                'https://d348w3g6ndshex.cloudfront.net', object_key)

            # Generate a signed URL for the object using CloudFront
            # signed_url = self.cloudfront_client.get_signed_url(
            #     DistributionId=self.cloudfront_distribution_id,
            #     Key=object_key,
            #     ExpiresIn=3600 * 2,  # Set the expiration time in seconds
            # )
            print("s3_objects: ", signed_url)

            if signed_url:
                signed_urls.append(signed_url)

        return signed_urls

    def getSignedUrl(self, distribution_domain, object_key):
        signed_url = ''
        key_pair_id = os.environ.get('KEY_PAIR_ID')
        expiresIn = datetime.now() + timedelta(hours=3)
        url = f"{distribution_domain}/{object_key}"

        try:
            cloudfront_signer = CloudFrontSigner(
                key_pair_id, self.rsa_signer)
            # Create a signed url that will be valid until the specific expiry date
            # provided using a canned policy.
            if cloudfront_signer:
                signed_url = cloudfront_signer.generate_presigned_url(
                    url, date_less_than=expiresIn)

        except Exception as ex:
            logging.error(f"cloudfront_signer error: {ex}")

        # cloudfront_signed_url = f'{signed_url}'

        # print('cloudfront_signed_url: ', cloudfront_signed_url)

        return signed_url if signed_url else ''

    def rsa_signer(self, message):
        BASE_DIR = Path(__file__).resolve().parent.parent
        env_file = os.path.join(BASE_DIR, 'private_key.pem')
        try:
            with open(env_file, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())
        except Exception as ex:
            logging.error(f"rsa_signer error: {ex}")
            return ''


@dataclass
class GoogleImageStore(ImageStore):
    repo: StorageRepoABC
    blob_list: list = list

    # def __init__(self, repo: StorageRepoABC) -> None:
    #     self.repo = repo
    #     self.blob_list: list

    def get_images(self):
        return ['https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame229.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame230.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame231.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame241.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321460.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321461.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321462.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321463.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321464.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321465.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321466.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321467.png',
                'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321468.png']

    # @lru_cache
    def list_images_in_bucket(self) -> list:
        bucket = self.repo.gcs_client.get_bucket(self.repo.bucket_name)

        # List all files in the folder by specifying a prefix
        self.blob_list = bucket.list_blobs(prefix=self.repo.path)
        return self.blob_list

    def generate_signed_url(self, blob, expiration):
        if blob.content_type.startswith('image/'):
            # Check if the blob represents an image (based on its content type)
            # If it's an image, generate a signed URL that is valid for the specified duration
            return blob.generate_signed_url(expiration=expiration)

        return None  # Return None for non-image blobs

    def generate_signed_urls(self) -> list:
        """Generate signed URLs to access private objects in a bucket concurrently."""

        signed_image_urls = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use the ThreadPoolExecutor for concurrent execution
            future_to_blob = {executor.submit(
                self.generate_signed_url, blob, self.repo.expiration): blob for blob in self.blob_list}

            for future in concurrent.futures.as_completed(future_to_blob):
                blob = future_to_blob[future]
                try:
                    signed_url = future.result()
                    if signed_url is not None:
                        signed_image_urls.append(signed_url)
                except Exception as ex:
                    logging.error(f"Error generating signed URL: {ex}")

        return signed_image_urls


class CacheRepo(ABC):

    @abstractmethod
    def getCacheItem(self):
        pass

    @abstractmethod
    def setCacheItem(self):
        pass


@dataclass
class RedisCache(CacheRepo):
    # cache = caches['autocomplete_redis_cache']
    # key: str = "query_store"

    def getCacheItem(self, key: str) -> dict | list:
        return self.cache.get(key)

    def setCacheItem(self, key: str, data):
        self.cache.set(key, data)

    # def generate_signed_urls(self) -> list:
    #     """Generate a signed URL to access a private object in a bucket."""
    #     # Generate signed URLs for each image

    #     signed_image_urls = []
    #     try:
    #         for blob in self.blob_list:
    #             if blob.content_type.startswith('image/'):
    #                 # Generate a signed URL that is valid for 1 * 3 hours (3600 seconds)
    #                 # print('blob_list', blob.public_url)

    #                 signed_url = blob.generate_signed_url(
    #                     expiration=self.repo.expiration)
    #                 # print("signed_url: ", signed_url)
    #                 signed_image_urls.append(signed_url)

    #     except Exception as ex:
    #         logging.error(f"generate_signed_urls {ex}")

    #     return signed_image_urls
