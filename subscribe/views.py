import base64
import datetime
import io
import json
from django.http import Http404
from django.shortcuts import render
import requests
import os
from django.conf import settings
from google.oauth2 import service_account
from google.cloud import secretmanager, logging
import logging as log
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceCredentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import json
import hmac
import hashlib
from rest_framework import mixins, generics, status
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from student.models import Student
from .models import Subscribe, Plan, Discount, Product, AppleNotify, Grade
from .serializers import (SubscribeSerializer, PlanSerializer, 
                          DiscountSerializer, ProductSerializer, InAppPaymentSerializer, AppleNotifySerializer, AndroidNotifySerializer)

# Create your views here.
class ListCreateUpdateAPISubscribe(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Subscribe.objects.all().order_by('user')
    serializer_class = SubscribeSerializer
    lookup_field = 'pk'
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

class ListCreateUpdateAPIPlan(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Plan.objects.all().order_by('amount')
    serializer_class = PlanSerializer
    lookup_field = 'pk'
    # ordering_fields = ['duration']

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

class ListCreateUpdateAPIDiscount(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Discount.objects.all().order_by('name')
    serializer_class = DiscountSerializer
    lookup_field = 'pk'
    ordering_fields = ['value']

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)
    

class ListCreateUpdateAPIBillingProduct(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Product.objects.all().order_by('pk')
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        response = self.list(request, *args, **kwargs)
        # print(response.data)
        return response

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def VerifyPurchase(request, *args, **kwargs):
    resp = result = {}
    response = {}
    response_json = {}
    user = None
    receipt_data = ''
    payment = None
    state = status.HTTP_400_BAD_REQUEST
    # receipt_data = request.data.get('receipt-data')
    purchase_data = request.data.get('purchase-data')
    is_sandbox = request.data.get('is_sandbox')
    grade = request.data.get('grade')
    platform = request.data.get('platform')
    # print('RECEIPT: ', receipt_data)
    # if platform == 'android':
    #     return verifyAndroidPurchase(purchase_data)
    if platform == 'ios':
        receipt_data = purchase_data.get('transactionReceipt')
    """
    Verify the purchase receipt data with the app store server and return the
    purchase details if the receipt is valid.

    Args:
    - receipt_data: str - the base64-encoded receipt data from the app store
    - is_sandbox: bool - whether the receipt is from a sandbox environment or not

    Returns:
    - dict - the purchase details if the receipt is valid, or None if invalid
    """

    # Set the appropriate endpoint URL based on whether the receipt is from a sandbox environment or not
    endpoint_url = 'https://buy.itunes.apple.com/verifyReceipt' if not is_sandbox else 'https://sandbox.itunes.apple.com/verifyReceipt'

    # Send a POST request to the app store server with the receipt data
    if platform == 'ios' and receipt_data:
        data = {"receipt-data": receipt_data, "password": '7f64d85b4b2046e6b0e2499e512d6c31'}
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(endpoint_url, json=data, headers=headers)
        # print('RECEIPT: ', response.json())

    # If the status code is not 200, the receipt is invalid
    if platform == 'ios' and response and response.status_code != 200:
        return Response(response.json(), status=response.status_code)

    # Parse the response JSON
    if platform == 'ios' and response:
        response_json = response.json()

    # If the response status is not 0, the receipt is invalid
    if platform == 'ios' and response_json and response_json.get('status') != 0:
        return Response(response_json, status.HTTP_400_BAD_REQUEST)

    # Get the purchase details from the response JSON
    if platform == 'ios':
        result = validate_in_app(response_json)
    if platform == 'android':
        resp = verifyAndroidPurchase(purchase_data, is_sandbox)
        result = resp
        state = status.HTTP_200_OK
    
    if result and result.get('transaction_id'):
        # product_id = result.get('product_id')
        # try:
        product_id = purchase_data.get('productId')
        

        try:
            print('purchase: ', result)
            product = Product.objects.get(product_id=product_id)
            payment_serializer = InAppPaymentSerializer(data=result)
            payment_serializer.is_valid(raise_exception=True)
            payment = payment_serializer.save(product=product)
            resp = payment_serializer.data
        except Exception as ex:
            #  status.HTTP_409_CONFLICT
             print(f'payment_serializer exception occurred: {ex}')
        
        if platform == 'ios':
            resp['status'] = response_json.get('status')
            state = status.HTTP_200_OK

        data = {
            "user": None,
            "product": None, 
            "payment_method": None,
            "grade": None
        }

        try:
            grade = Grade.objects.get(pk=grade)
            if not request.user.is_anonymous:
                user = request.user
        except Exception as ex:
            print(f'Grade exception occurred: {ex}')
            
        try:
            if payment and product and grade and user:
                subscribe_serializer = SubscribeSerializer(data=data)
                subscribe_serializer.is_valid(raise_exception=True)
                subscribe_serializer.save(user = user, product=product, payment_method=payment, grade=grade)
                state = status.HTTP_201_CREATED

        except Exception as ex:
            print(f'SubscribeSerializer exception occurred: {ex}')
    
    # print('RESPONSE: ', resp)
    return Response(resp, state)

def verifyAndroidPurchase(purchase, isSandBox):
    subscription_id = purchase.get('productId')
    purchase_token = purchase.get('purchaseToken')
    package_name = purchase.get('packageNameAndroid')
    # response = verifyAndroidPayment(subscription_id, purchase_token, package_name, isSandBox)
    
    # return Response(response)
    
    return verify_android_purchase(purchase_token, subscription_id, package_name, isSandBox)

def validate_in_app(receipt_json_data):
    response = {}
    gateway = 'Apple In-App'
    expires_date = ""
    expiration_intent = ""
    original_transaction_id2 = ""
    original_transaction_id = ''
    posix_date_time = ''
    product_id = ''
    transactionDate = ''
    in_app_ownership_type = ''
    auto_renew_status = ''

    if receipt_json_data:
        environment = receipt_json_data.get('environment')
        latest_receipt_info = receipt_json_data.get('latest_receipt_info', {})
        pending_renewal_info = receipt_json_data.get('pending_renewal_info', {})


        if len(latest_receipt_info) > 0:
            original_transaction_id = latest_receipt_info[0].get('original_transaction_id')
            transaction_id = latest_receipt_info[0].get('transaction_id')
            posix_date_time = latest_receipt_info[0].get('purchase_date_ms')
            expires_date = latest_receipt_info[0].get('expires_date_ms')
            product_id = latest_receipt_info[0].get('product_id')

        else:
            inapp = receipt_json_data.get('in_app', {})
            if inapp:
                transaction_id = inapp[0].get('transaction_id')
                posix_date_time = inapp[0].get('purchase_date_ms')
                product_id = inapp[0].get('product_id')
                original_transaction_id = inapp[0].get('original_transaction_id')
                in_app_ownership_type = inapp[0].get('in_app_ownership_type')

        if pending_renewal_info:
            original_transaction_id2 = pending_renewal_info[0].get('original_transaction_id')
            auto_renew_status = pending_renewal_info[0].get('auto_renew_status')
            expiration_intent = pending_renewal_info[0].get('expiration_intent')

        if not original_transaction_id and original_transaction_id2:
                original_transaction_id = original_transaction_id2

        if posix_date_time:
            transactionDate = datetime.datetime.fromtimestamp(float(posix_date_time)/1000.0)

        purchase_details = {
            'name': gateway,
            # 'product_id': product_id,
            'environment': environment,
            'original_transaction_id': original_transaction_id,
            'transaction_id': transaction_id,
            'expires_date': convertDateFromMSToDateTime(expires_date),
            'expiration_intent': expiration_intent,
            'in_app_ownership_type': in_app_ownership_type,
            'auto_renew_status': auto_renew_status,
            'original_purchase_date': transactionDate
        }
        response = purchase_details

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def AppStoreNotificationHandler(request, *args, **kwargs):
    if request.method == 'POST':
        envelope = request.data
        message = envelope.get("signedPayload")
        apple_notify_iap(message)

    return Response(status.HTTP_200_OK)

def apple_notify_iap(message):
    # response = {}
    signed_transaction_info = signed_renewal_info = decoded_payload_transaction_info = decoded_payload_signed_renewal_info = None
    decoded_header, decoded_payload, decoded_signature = decode_transaction(message)
    
    if decoded_payload:
        decoded_payload = json.loads(decoded_payload)
        # print('decoded_payload: ', decoded_payload)
        notification_type = decoded_payload.get("notificationType")
        decoded_payload_data = decoded_payload["data"]
        if decoded_payload_data:
            bundle_id = decoded_payload_data.get("bundleId")
            environment = decoded_payload_data.get("environment")
            signed_transaction_info = decoded_payload_data.get("signedTransactionInfo")
            signed_renewal_info = decoded_payload_data.get("signedRenewalInfo")

        if signed_transaction_info:
            decoded_header_transaction_info, decoded_payload_transaction_info, decoded_signature_transaction_info = decode_transaction(signed_transaction_info)

        if signed_renewal_info:
            decoded_header_signed_renewal_info, decoded_payload_signed_renewal_info, decoded_signature_signed_renewal_info = decode_transaction(signed_renewal_info)

        if decoded_payload_transaction_info:
            decoded_payload_transaction_info = json.loads(decoded_payload_transaction_info)

        if decoded_payload_signed_renewal_info:
            decoded_payload_signed_renewal_info = json.loads(decoded_payload_signed_renewal_info)
            message = ''

        if decoded_payload_transaction_info and decoded_payload_signed_renewal_info:
            verify_apple_pay(notification_type, bundle_id, environment, decoded_payload_transaction_info, decoded_payload_signed_renewal_info, decoded_signature, message)

    # return response

def decode_transaction(signed_info):
    header, payload, signature = "", "", ""
    decoded_header, decoded_payload, decoded_signature = "", "", ""
    signedInfo = signed_info.split(".")
    if len(signedInfo) > 2:
            for i in range(len(signedInfo)):
                if i == 0:
                    header = signedInfo[i]
                elif i == 1:
                    payload = signedInfo[i]
                elif i == 2:
                    signature = signedInfo[i]
    if header:
        decoded_header = pad_encoded_data(header)
    if payload:
        decoded_payload = pad_encoded_data(payload)
    #if signature:
        #decoded_signature = pad_encoded_data(signature)

    return decoded_header, decoded_payload, decoded_signature

def pad_encoded_data(data):
    padded = data + "="*divmod(len(data),4)[1]
    return base64.b64decode(padded)

def verify_apple_pay(notification_type, bundle_id, environment, jws_transaction_decodedPayload , jws_renewal_info_decodedPayload, decoded_signature, signedPayload):
    gateway = 'Apple In-App'
    expiration_intent = ""

    original_transaction_id = jws_transaction_decodedPayload.get('originalTransactionId')
    transaction_id = jws_transaction_decodedPayload.get('transactionId')
    posix_date_time = jws_transaction_decodedPayload.get('purchaseDate')
    expires_date = jws_transaction_decodedPayload.get('expiresDate')
    product_id = jws_transaction_decodedPayload.get('productId')
    original_transaction_id2 = jws_renewal_info_decodedPayload.get('originalTransactionId')
    auto_renew_status = jws_renewal_info_decodedPayload.get('autoRenewStatus')
    try:
        expiration_intent = jws_renewal_info_decodedPayload('expirationIntent')
    except:
        print('expiration_intent error!')

    if not original_transaction_id and original_transaction_id2:
        original_transaction_id = original_transaction_id2

    if original_transaction_id:
        transactionDate = datetime.datetime.fromtimestamp(float(posix_date_time)/1000.0)

        purchase_details = {
            'name': gateway,
            'product_id': product_id,
            'environment': environment,
            'original_transaction_id': original_transaction_id,
            'transaction_id': transaction_id,
            'expires_date': expires_date,
            'expiration_intent': expiration_intent,
            'auto_renew_status': auto_renew_status,
            'original_purchase_date': transactionDate
        }


        apple_notify = AppleNotifySerializer(data=purchase_details)
        apple_notify.is_valid(raise_exception=True)
        apple_notify.save()

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def PlayStoreNotificationHandler(request):
    state = status.HTTP_400_BAD_REQUEST
    response = {}
    if request.method == 'POST':
        msg = 'OK'
        envelope = request.data
        printOutLogs('ENVELOPE: ', envelope)

        if not envelope:
            msg = "no Pub/Sub message received"
            #printOutLogs(msg)
            return Response(data=f"Bad Request: {msg}", status=state)

        if not isinstance(envelope, dict) or "message" not in envelope:
            msg = "invalid Pub/Sub message format"
            #printOutLogs(msg)
            return Response(data=f"Bad Request: {msg}", status=state)

        pubsub_message = envelope.get("message")
        if isinstance(pubsub_message, dict) and "data" in pubsub_message and pubsub_message.get("data"):
            data = base64.b64decode(pubsub_message.get("data")).decode("utf-8").strip()
            printOutLogs('DATA: ', data)
            data = json.loads(data)
            packageName = data.get('packageName')
            if packageName == os.environ.get('PACKAGE_NAME'):
                set_android_pay(data, packageName)
            # if response and response.get('status') == status.HTTP_201_CREATED:
            state = status.HTTP_200_OK
        
    return Response(state)


# Define a view to handle webhook notifications
@csrf_exempt
def FlutterWaveWebhook(request):
    if request.method != 'POST':
        return Response('Invalid request method', status.HTTP_400_BAD_REQUEST)

    secret_hash = os.environ.get('FLUTTERWAVE_SECRET_HASH')
    secret_key = os.environ.get('FLUTTERWAVE_API_SECRET_KEY')

    # Verify the webhook signature
    signature = request.headers.get('verif-hash')
    if not signature:
        return Response('Missing signature', status.HTTP_400_BAD_REQUEST)

    computed_signature = hmac.new(
        secret_hash.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    if signature != computed_signature:
        return Response('Invalid signature', status.HTTP_400_BAD_REQUEST)

    # Process the webhook payload
    # payload = request.json()['data']
    payload = request.data.get('data')
    event = payload.get('event')

    if event == 'charge.completed':
        # Handle the completed payment event
        transaction_id = payload.get('id')
        transaction_verification_uri = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'
    
    # Send a GET request to the transaction verification URI with your Flutterwave API keys
        response = requests.get(transaction_verification_uri, headers={
            'Authorization': f"Bearer {secret_key}",
            'Content-Type': 'application/json'
        })
        # Extract the verification status from the response and update your database accordingly
        # verification_status = response.json()['data']['status']
        data = response.data.get('data')
        verification_status = amount = product = grade = student = user = payment = created = tx_ref = flw_ref = payment_type = ""
        purchase_details = meta = customer = {}

        if data:
            verification_status = data.get('status')
            created_at = data.get('created_at')
            amount = data.get('amount')
            tx_ref = data.get('tx_ref')
            flw_ref = data.get('flw_ref')
            payment_type = data.get('payment_type')
            meta = data.get('meta')
            customer = data.get('customer')


        if verification_status == 'successful':
            # ... process the payment ...
            created = dateStrToDateTime(created_at)
            purchase_details = {
                "name": "FlutterWave",
                "environment": "",
                "original_transaction_id": tx_ref,
                "transaction_id": transaction_id,
                "expires_date": "",
                "product": None,
                "auto_renew_status": flw_ref,
                "expiration_intent": "",
                "in_app_ownership_type": payment_type,
                "original_purchase_date": created
            }

        if amount and purchase_details:
            try:
                product = Product.objects.get(amount=float(f"{amount:.2f}"))
                expires_date = created + datetime.timedelta(days=product.duration)
                payment_serializer = InAppPaymentSerializer(data=purchase_details)
                payment_serializer.is_valid(raise_exception=True)
                payment = payment_serializer.save(product=product, expires_date=expires_date)
            except Exception as ex:
                print(f"payment serializer error: {ex}")
        
        if meta:
            try:
                grade_val = meta.get(grade)
                if isinstance(grade_val, int):
                    grade = Grade.objects.get(pk=grade)
                if isinstance(grade_val, str):
                    grade = Grade.objects.get(name=grade)
            except Exception as ex:
                print(f"grade error: {ex}")

        if customer:
            email = customer.get('email')
            try:
                user = User.objects.get(email=email)
            except Student.DoesNotExist:
                raise Http404
            
            if not user:
                phone_number = customer.get('phone_number')
                try:
                    student = Student.objects.get(phone_number=phone_number)
                    user = student.user
                except Student.DoesNotExist:
                    raise Http404

        if user and product and payment and grade:
            data = {
                "user": None,
                "product": None, 
                "payment_method": None,
                "grade": None
            }
            try:
                subscribe_serializer = SubscribeSerializer(data=data)
                subscribe_serializer.is_valid(raise_exception=True)
                subscribe_serializer.save(user = student.user, product=product, payment_method=payment, grade=grade)
            except Exception as ex:
                print(f"subscribe serializer error: {ex}")


    elif event == 'charge.failed':
        # Handle the payment failed event
        payment_id = payload.get('id')
        # TODO: handle the failed payment and update your database


    # Respond with a 200 status code to acknowledge receipt of the webhook
    return Response({'success': True}, status.HTTP_200_OK)

def set_android_pay(data, packageName):
    subscriptionNotification = data.get('subscriptionNotification')
    if subscriptionNotification:
        purchaseToken = subscriptionNotification.get('purchaseToken')
        subscriptionId = subscriptionNotification.get('subscriptionId')

        return verifyAndroidPayment(subscriptionId, purchaseToken, packageName)
    
    return {}

def verifyAndroidPayment(subscriptionId, purchase_token, packageName):
    amount = 0
    currency = "₦"
    state = status.HTTP_400_BAD_REQUEST
    result = purchase_details = {}
    country_code = 'NG'
    purchaseState = 1
    paymentState = 0
    purchase_date = paymentState = acknowledgementState = consumptionState = start_time = expiry = transaction_id = regionCode = priceAmountMicros = ""

    service_acct = os.environ.get("SERVICE_ACCOUNT", "SERVICE_ACCOUNT")
    purchase = build_service_credentials(service_acct, packageName, subscriptionId,  purchase_token)

    try:

        if purchase:
            startTimeMillis = purchase.get("startTimeMillis", '')
            expiryTimeMillis = purchase.get("expiryTimeMillis", '')
            purchaseTimeMillis = purchase.get("purchaseTimeMillis", '')
            currency = purchase.get("priceCurrencyCode", '')
            priceAmountMicros = purchase.get("priceAmountMicros") 
            country_code = purchase.get("countryCode", '')
            regionCode = purchase.get("regionCode", '')
            transaction_id = purchase.get("orderId")
            purchaseState = purchase.get("purchaseState", 1)
            acknowledgementState = purchase.get("acknowledgementState")
            consumptionState = purchase.get("consumptionState", 0)
            paymentState = purchase.get("paymentState", 0)

        if (purchaseState == 0 or paymentState == 1) and (acknowledgementState == 1 or consumptionState == 1):
            if startTimeMillis:
                start_time = convertDateFromMSToDateTime(startTimeMillis)
            if expiryTimeMillis:
                expiry = convertDateFromMSToDateTime(expiryTimeMillis)
            if purchaseTimeMillis:
                purchase_date = convertDateFromMSToDateTime(purchaseTimeMillis)
            if priceAmountMicros:
                amount = int(priceAmountMicros) / 1000000
            if not country_code:
                country_code = regionCode

        purchase_details = {
            'subscription_Id': subscriptionId,
            'purchase_token': purchase_token,
            'transaction_id': transaction_id,
            'expires_date': expiry,
            'purchaseState': purchaseState,
            'acknowledgementState': acknowledgementState,
            'consumptionState': consumptionState,
            'paymentState': paymentState,
            'country_code': country_code,
            'regionCode': regionCode,
            'purchase_date': purchase_date,
            'start_time': start_time,
            'amount': amount,
            'currency': currency,
        }
    except Exception as ex:
        print('PURCHASE: ', ex)
        printOutLogs('PURCHASE: ', ex)

    try:
        if purchase_details:
            # resp = status.HTTP_201_CREATED
            android_notify = AndroidNotifySerializer(data=purchase_details)
            android_notify.is_valid(raise_exception=True)
            notify = android_notify.save()
            # if notify.transaction_id: 
            state = status.HTTP_201_CREATED

    except Exception as ex:
        print('NOTIFY: ', ex)
        printOutLogs('NOTIFY: ', ex)

    result['status'] = 0
    return {'result' : purchase, 'status': state}



# Function to verify Android in-app subscriptions and purchases
def verify_android_purchase(purchase_token: str, subscription_id: str, package_name: str, isSandBox: bool=True) -> dict:
    purchase_details = {}
    secret_name = os.environ.get('Google-Play-Android', 'Google-Play-Android')
    # Load the service account credentials
    purchase = build_service_credentials(secret_name, package_name, subscription_id,  purchase_token)
    # print('purchase: ', purchase)

    try:
        if purchase and (purchase.get("purchaseState", 1) == 0 or purchase.get("paymentState", 0) == 1) and (purchase.get("acknowledgementState", 0) == 1 or purchase.get("consumptionState", 0)) == 1:
            # Purchase or subscription is valid
            purchase_details = {
                "name": "Android In-App",
                "environment": str(isSandBox),
                "original_transaction_id": purchase_token,
                "transaction_id": purchase.get("orderId"),
                "expires_date": convertDateFromMSToDateTime(purchase.get("expiryTimeMillis", datetime.datetime.now())),
                "product": None,
                "auto_renew_status": str(purchase.get("autoRenewing", 1)),
                "expiration_intent": "",
                "in_app_ownership_type": purchase.get("purchaseType"),
                "original_purchase_date": convertDateFromMSToDateTime(purchase.get("purchaseTimeMillis", '')),
                "status" : 0,
                "created": convertDateFromMSToDateTime(purchase.get("startTimeMillis", datetime.datetime.now()))
            }

        elif purchase and (purchase.get("purchaseState", 1) == 0 or purchase.get("paymentState", 0) == 1) and (purchase.get("acknowledgementState", 0) == 0 or purchase.get("consumptionState", 0)) == 1:
            purchase_details = {
                "status": 0
            }
        else:
            # Purchase or subscription is not valid
            pass

    except HttpError as error:
        # Error occurred while verifying the purchase or subscription
        print(f'An error occurred: {error}')
        # return Response(result)
    # except Exception as ex:
    #     print(f'CREDENTIAL exception occurred: {ex}')

    return purchase_details

def build_service_credentials(secret_name, packageName, subscriptionId, purchase_token):
    purchase = {}
    try:
        if secret_name and packageName and subscriptionId and purchase_token:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{settings.PROJECT_ID}/secrets/{secret_name}/versions/latest"
            payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
            # print('payload: ', type(payload))
            service_credentials_dict = json.loads(payload)
            service_credentials = ServiceCredentials.from_service_account_info(service_credentials_dict)
            credentials = service_credentials.with_scopes(['https://www.googleapis.com/auth/androidpublisher'])
            service = build("androidpublisher", "v3", credentials=credentials)
        
            purchase = service.purchases().subscriptions().get(packageName=packageName, subscriptionId=subscriptionId, token=purchase_token).execute()

    
    except Exception as ex:
        print(f'A BUILD_SERVICE_CREDENTIALS exception occurred: {ex}')

    return purchase

def printOutLogs(tag='', param=''):
    logging_client = logging.Client()
    logging_client.get_default_handler()
    logging_client.setup_logging()
    log.info(f"Some log here: {tag} : {param}") 


def convertDateFromMSToDateTime(ms_date_time):
    transactionDate = None
    if ms_date_time:
        transactionDate = datetime.datetime.fromtimestamp(float(ms_date_time)/1000.0)   
    return transactionDate

def dateStrToDateTime(date_str, date_format="%d %m %Y %H:%M:%S"):
    date_obj = ""
    if date_str:
        date_obj = datetime.strptime(date_str, date_format)

    return date_obj

# Define a function to verify the webhook signature
def verify_webhook_signature(payload, signature, FLUTTERWAVE_SECRET_KEY):
    # Convert the secret key to bytes
    secret_key = bytes(FLUTTERWAVE_SECRET_KEY, 'utf-8')
    # Compute the HMAC-SHA256 hash of the payload using the secret key
    computed_signature = hmac.new(secret_key, payload, hashlib.sha256).hexdigest()
    # Compare the computed signature to the signature from the webhook header
    return hmac.compare_digest(computed_signature, signature)


