from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from course.models import Grade
from twilio.rest import Client as twiClient
from .views import sms_messaging

User = get_user_model()

# Create your tests here.

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sms_messaging(self):
        response = sms_messaging()
        print(response.status)
        self.assertEqual(response.status, 'approved')


