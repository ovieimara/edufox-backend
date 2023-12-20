from venv import logger
from django.shortcuts import render
from django.contrib.auth.models import User
import requests
from twilio.rest import Client as twiClient
from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Email, Personalization
import os

from sendgrid.helpers.mail import Mail, Email, To, Content

from edufox.views import printOutLogs


# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC31285f7730586b37af4cb9ebb195cbb8"
# account_sid = "ACfe52cd18a7ec3c5ceff874f660e8bdfe"
auth_token = "263641b76fe494e77a309aa07b1675d2"
# auth_token = "afa0ebdb9dd4f10760ac35001ba5443f"
verify_sid = "VA62d99c100a8c0b9a978aa691f699b0fc"
verified_number = "+2347048536974"
# verified_number = "+2348023168805"


# client = twiClient(account_sid, os.environ.get("auth_token"))
client = twiClient(account_sid, auth_token)


# Create your views here.

def sms_messaging():
    otp_code = input("Please enter the OTP:")


def createOTP(phone_number):
    verification = None
    try:
        verification = client.verify.v2.services(verify_sid) \
            .verifications \
            .create(to=phone_number, channel="sms")
        printOutLogs('createOTP: ', verification.status)
    except Exception as ex:
        print('SMS OTP creation error: ', ex)

    return verification


def verifyOTP(otp, phone_number):
    verification_check = None
    try:
        verification_check = client.verify.v2.services(verify_sid) \
            .verification_checks \
            .create(to=phone_number, code=otp)

    except Exception as ex:
        print('SMS OTP verify error: ', ex)

    return verification_check


def emailOTP(email):
    verification = None
    try:
        verification = client.verify.v2.services(verify_sid) \
            .verifications \
            .create(to=email, channel='email')

    except Exception as ex:
        print('Email OTP creation error: ', ex)

    return verification


def verifyEmail(otp, email):
    verification_check = None
    try:
        verification_check = client.verify \
            .v2 \
            .services(verify_sid) \
            .verification_checks \
            .create(to=email, code=otp)

    except Exception as ex:
        print('Email OTP verify error: ', ex)

    return verification_check

    template_id = "d-4813742d049247109c9ec38ee94c13cd"


template = "d-4813742d049247109c9ec38ee94c13cd"


def send_email_with_template(substitutions: dict, template_id: str = "d-⁠4813742d049247109c9ec38ee94c13cd"):
    """Sends an email using the SendGrid API with a template.

    Args:
      sendgrid_api_key: Your SendGrid API key.
      template_id: The ID of the SendGrid template to use.
      to_email: The email address of the recipient.
      substitutions: A dictionary of substitutions to make in the template.

    Returns:
      A response object from the SendGrid API.
    """
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

    # print("sendgrid_api_key: ", sendgrid_api_key)

    message = Mail(
        from_email=substitutions.get('from_email'),
        to_emails=substitutions.get('to_email'),
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    message.dynamic_template_data = {
        'subject': substitutions.get('subject'),
        'name': substitutions.get('name'),
        'message': substitutions.get('message')
    }
    message.template_id = template_id
    try:
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        return sendgrid_client.send(message)
    except Exception as ex:
        logger.error(f"send_email_with_template Error: {ex}")
