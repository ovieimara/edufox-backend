from abc import ABC, abstractmethod
import os
from venv import logger
from PIL import Image

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from student.models import Student
from .serializers import FileUploadSerializer


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
            tmp_image_path = self.resize_image(file, new_width, new_height)
            # Save the file to Google Cloud Storage
            public_url = self.save_file_to_cloud_storage(tmp_image_path, file)
            self.update_student(self, public_url, user)

            return Response({'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def resize_image(self, file, new_width, new_height):
        # Open the image using Pillow
        image = Image.open(file)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)

        dpi = self.reduce_resolution(image)
        # Save the processed image to a temporary file
        # Adjust the path and format as needed
        tmp_image_path = '/tmp/processed_image.jpg'
        image.save(tmp_image_path, 'JPEG', dpi=dpi)
        return tmp_image_path

    def reduce_resolution(self, image):
        # Reduce the resolution by changing DPI (dots per inch)
        dpi = (72, 72)  # Set the desired DPI
        image.info['dpi'] = dpi
        return dpi

    def save_file_to_cloud_storage(self, tmp_image_path, file):
        # Upload the processed image to Google Cloud Storage
        # Adjust the path and filename as needed
        gcs_path = 'path/in/bucket/processed_image.jpg'

        # Save the file to Google Cloud Storage
        with open(tmp_image_path, 'rb') as tmp_image:
            file.storage.save(gcs_path, tmp_image)

        return file.storage.url(gcs_path)

    def clean_temp_file(self, tmp_image_path):
        # Clean up the temporary file
        os.remove(tmp_image_path)

    def update_student(self, public_url, user):

        try:
            student = Student.objects.get(phone_number=user.username)
        except student.DoesNotExist as ex:
            logger.error('File upload: ', ex)

        if student and public_url:
            student.save(image_url=public_url)


class ImageScaler(ABC):
    def __init__(self, file, new_width, new_height) -> None:
        super().__init__()

    @abstractmethod
    def resize(self):
        pass

    @abstractmethod
    def reduce_resolution(self, image):
        pass


class ImageStore(ABC):
    def save(self):
        pass
