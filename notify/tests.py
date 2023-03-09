from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from course.models import Grade
from twilio.rest import Client as twiClient
from .views import sms_messaging, emailOTP, verifyEmail, createOTP, verifyOTP

User = get_user_model()

# Create your tests here.

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    # def test_email_verify(self):
    #     phone = "+2347048536974"
    #     response = createOTP(phone)
    #     otp = input('input otp: ')
    #     response = verifyOTP(otp, phone)
    #     print(response.sid)

    # def test_email_verify(self):
    #     email = 'imaraovie@gmail.com'
    #     response = emailOTP(email)
    #     otp = input('input otp: ')
    #     response = verifyEmail(otp, email)
    #     print(response.sid)

    # def test_sms_messaging(self):
    #     response = sms_messaging()
    #     print(response.status)
    #     self.assertEqual(response.status, 'approved')



