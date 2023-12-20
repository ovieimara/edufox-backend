from abc import ABC, abstractmethod
# from hashlib import file_digest
import os
from typing import Any
from venv import logger
from PIL import Image
from dataclasses import dataclass
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from google.cloud import storage
from edufox.views import printOutLogs
from student.models import Student
from .serializers import FileUploadSerializer
from django.contrib.auth.models import User


class FileUploadView(APIView):
    # permission_classes = []

    def post(self, request, format=None):
        data = request.data
        printOutLogs("data: ", data)
        serializer = FileUploadSerializer(data=data)
        user = request.user
        public_url = ''
        ext = 'png'
        if user.is_authenticated and serializer.is_valid():
            file = serializer.validated_data['file']
            # Resize the image to a specific width and height
            new_width = 800
            new_height = 600
            pk = user.pk
            resizer = PillowResizer(file, new_width, new_height)
            image = resizer.resize()
            dpi = resizer.reduce_resolution(image)
            tmp_image_path = resizer.save(image, dpi, pk, ext)
            # tmp_image_path = self.resize_image(file, new_width, new_height)
            # Save the file to Google Cloud Storage
            gcs_path = f'img/profile/{pk}.{ext}'
            bucket_name = "edufox-bucket-2"
            cloud_store = GoogleStore(
                file, tmp_image_path, gcs_path, bucket_name)
            public_url = cloud_store.save_to_storage(ext)
            # public_url = self.save_file_to_cloud_storage(tmp_image_path, file)
            # print('URL', public_url)
            self.update_student(public_url, user.username)
            self.clean_temp_file(tmp_image_path)

            return Response({'image_url': public_url, 'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # def resize_image(self, file, new_width, new_height):
    #     # Open the image using Pillow
    #     image = Image.open(file)
    #     image = image.resize((new_width, new_height), Image.ANTIALIAS)

    #     dpi = self.reduce_resolution(image)
    #     # Save the processed image to a temporary file
    #     # Adjust the path and format as needed
    #     tmp_image_path = '/tmp/processed_image.jpg'
    #     image.save(tmp_image_path, 'JPEG', dpi=dpi)
    #     return tmp_image_path

    # def reduce_resolution(self, image):
    #     # Reduce the resolution by changing DPI (dots per inch)
    #     dpi = (72, 72)  # Set the desired DPI
    #     image.info['dpi'] = dpi
    #     return dpi

    # def save_file_to_cloud_storage(self, tmp_image_path, file):
    #     # Upload the processed image to Google Cloud Storage
    #     # Adjust the path and filename as needed
    #     gcs_path = 'path/in/bucket/processed_image.jpg'

    #     # Save the file to Google Cloud Storage
    #     # with open(tmp_image_path, 'rb') as tmp_image:
    #     #     file.storage.save(gcs_path, tmp_image)
    #     store = GoogleStore(file, tmp_image_path, gcs_path)
    #     return store.save()

        # return file.storage.url(gcs_path)

    def clean_temp_file(self, tmp_image_path: str):
        # Clean up the temporary file
        os.remove(tmp_image_path)

    def update_student(self, public_url: str, user: str):
        student = ''
        # print('USER: ', user.username)
        try:
            student = Student.objects.get(phone_number=user)
        except student.DoesNotExist as ex:
            logger.error('File upload: ', ex)

        if student and public_url:
            student.image_url = public_url
            student.save()

        print('STUDENT: ', student.image_url)


class Resizer(ABC):

    def save(self, image: Image, dpi: tuple[int, int], pk: int, ext: str) -> str:
        # Save the processed image to a temporary file
        # Adjust the path and format as needed
        tmp_image_path = f'/tmp/pk.{ext}'
        image.save(tmp_image_path, ext, dpi=dpi)
        return tmp_image_path

    @abstractmethod
    def resize(self) -> Image:
        pass

    @abstractmethod
    def reduce_resolution(self) -> tuple[int, int]:
        pass


@dataclass
class PillowResizer(Resizer):
    file: Any
    new_width: int
    new_height: int

    def reduce_resolution(self, image: Image) -> tuple[int, int]:
        # Reduce the resolution by changing DPI (dots per inch)
        dpi = (72, 72)  # Set the desired DPI
        image.info['dpi'] = dpi
        return dpi

    def resize(self) -> Image:
        image = Image.open(self.file)
        image = image.resize(
            (self.new_width, self.new_height), Image.LANCZOS)
        return image
        # dpi = self.reduce_resolution(image)
        # self.save(image, dpi)


class Store(ABC):
    def save_to_storage(self):
        pass


@dataclass
class GoogleStore(Store):
    file: Any
    tmp_image_path: str
    gcs_path: str
    bucket_name: str

    def save_to_storage(self, ext: str):
        # Save the file to Google Cloud Storage
        with open(self.tmp_image_path, 'rb') as image_file:
            file_content = image_file.read()

        # Upload to Google Cloud Storage
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(self.gcs_path)
        blob.upload_from_string(file_content, content_type=f'image/{ext}')

        # Construct the URL based on the bucket and path
        base_url = f'https://storage.googleapis.com/edufox-bucket-2/'
        image_url = f'{base_url}{self.gcs_path}'  # Full image URL
        # print(image_file)
        return image_url
