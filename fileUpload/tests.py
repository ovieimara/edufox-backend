from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import io

from course.tests import User
from student.models import Student


class FileUploadViewTests(TestCase):
    url = reverse('fileUpload:file-upload')

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            is_staff=True,
            username='testuser',
            email='testuser@example.com',
            password='password@123A',
        )
        self.user.is_staff = True
        self.user.save()

        self.user2 = User.objects.create_user(
            # is_staff=True,
            username='+23407048536974',
            email='testuser@example.com',
            password='password@123A'
        )

        Student.objects.create(
            phone_number='+23407048536974',
            user=self.user2,
            referral_id=None,
            image_url=''
        )

    def _create_image(self, width, height):
        # Create a test image
        image = Image.new('RGB', (width, height))
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return image_io

    def test_file_upload(self):
        # Create a temporary image file for testing
        image = self._create_image(200, 200)

        # Prepare the payload
        data = {'file': image}

        # Make the API call
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(self.url, data, format='multipart')

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('File uploaded successfully',
                      str(response.data))

        # Clean up (optional)
        image.close()

    # def test_invalid_file_upload(self):
    #     # Try to upload a non-image file (e.g., a text file)
    #     data = {'file': open('path/to/invalid_file.txt', 'rb')}

    #     # Make the API call
    #     response = self.client.post(self.url, data, format='multipart')

    #     # Assert the response
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
