from django.shortcuts import render
from django.contrib.auth.models import User
from twilio.rest import Client as twiClient
import os


# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC31285f7730586b37af4cb9ebb195cbb8"
# account_sid = "ACfe52cd18a7ec3c5ceff874f660e8bdfe"
auth_token = "263641b76fe494e77a309aa07b1675d2"
# auth_token = "afa0ebdb9dd4f10760ac35001ba5443f"
verify_sid = "VA62d99c100a8c0b9a978aa691f699b0fc"
verified_number = "+2347048536974"
# verified_number = "+2348023168805"


client = twiClient(account_sid, os.environ.get("auth_token"))

# Create your views here.

def sms_messaging():
    otp_code = input("Please enter the OTP:")

def createOTP(phone_number):
    verification = client.verify.v2.services(verify_sid) \
    .verifications \
    .create(to=phone_number, channel="sms")
    print(verification.status)

def verifyOTP(otp):
    verification_check = client.verify.v2.services(verify_sid) \
    .verification_checks \
    .create(to=verified_number, code=otp)
    return verification_check