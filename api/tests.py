from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_swagger_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
