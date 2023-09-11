from abc import ABC, abstractmethod
from hashlib import file_digest
import os
from typing import Any
from venv import logger
from PIL import Image
from attr import dataclass

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from student.models import Student
from .serializers import FileUploadSerializer
from django.contrib.auth.models import User


class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        user = request.user
        public_url = ''
        if user.is_authenticated and serializer.is_valid():
            file = serializer.validated_data['file']
            # Resize the image to a specific width and height
            new_width = 800
            new_height = 600

            resizer = PillowResizer(file, new_width, new_height)
            image = resizer.resize()
            dpi = resizer.reduce_resolution(image)
            tmp_image_path = resizer.save(image, dpi)
            # tmp_image_path = self.resize_image(file, new_width, new_height)
            # Save the file to Google Cloud Storage
            gcs_path = 'path/in/bucket/processed_image.jpg'
            cloud_store = GoogleStore(file, tmp_image_path, gcs_path)
            public_url = cloud_store.save()
            public_url = self.save_file_to_cloud_storage(tmp_image_path, file)

            self.update_student(self, public_url, user)
            self.clean_temp_file(tmp_image_path)
            return Response({'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def update_student(self, public_url: str, user: User):

        try:
            student = Student.objects.get(phone_number=user.username)
        except student.DoesNotExist as ex:
            logger.error('File upload: ', ex)

        if student and public_url:
            student.save(image_url=public_url)


class Resizer(ABC):

    def save(self, image: Image, dpi: tuple[int, int]) -> str:
        # Save the processed image to a temporary file
        # Adjust the path and format as needed
        tmp_image_path = '/tmp/processed_image.png'
        image.save(tmp_image_path, 'PNG', dpi=dpi)
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
            (self.new_width, self.new_height), Image.ANTIALIAS)
        return image
        # dpi = self.reduce_resolution(image)
        # self.save(image, dpi)


class Store(ABC):
    def save(self):
        pass


@dataclass
class GoogleStore(Store):
    file: Any
    tmp_image_path: str
    gcs_path: str

    def save(self) -> str:
        with open(self.tmp_image_path, 'rb') as self.tmp_image:
            self.file.storage.save(self.gcs_path, self.tmp_image)

        return self.file.storage.url(self.gcs_path)
