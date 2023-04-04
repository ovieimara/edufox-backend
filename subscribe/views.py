import base64
import datetime
import json
from django.shortcuts import render
import requests
from rest_framework import mixins, generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Subscribe, Plan, Discount, Product, AppleNotify
from .serializers import (SubscribeSerializer, PlanSerializer, 
                          DiscountSerializer, ProductSerializer, InAppPaymentSerializer, AppleNotifySerializer)

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

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)
    
@api_view(['POST'])
def verify_purchase(request, *args, **kwargs):
    resp = None
    response = None
    response_json = None
    receipt_data = request.data.get('receipt_data')
    is_sandbox = request.data.get('is_sandbox')
    grade = request.data.get('grade')

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
    if receipt_data:
        response = requests.post(endpoint_url, json={'receipt-data': receipt_data})

    # If the status code is not 200, the receipt is invalid
    if response and response.status_code != 200:
        return None

    # Parse the response JSON
    if response:
        response_json = response.json()

    # If the response status is not 0, the receipt is invalid
    if response_json and response_json.get('status') != 0:
        return None

    # Get the purchase details from the response JSON
    result = validate_in_app(response_json)

    if result and result.get('product_id'):
        product_id = result.get('product_id')
        product = Product.objects.get(product_id=product_id)
        payment_serializer = InAppPaymentSerializer(data=result)
        payment_serializer.is_valid(raise_exception=True)
        payment_serializer.save(product=product)
        resp = payment_serializer.data

        data = {
            "user": None,
            "product": None, 
            "payment_method": None,
            "grade": None
        }
        subscribe_serializer = SubscribeSerializer(data=data)
        subscribe_serializer.is_valid(raise_exception=True)
        subscribe_serializer.save(user = request.user, product=product, payment_method=payment_serializer, grade=grade)

    return Response(resp, status.HTTP_200_OK)


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
            expires_date = latest_receipt_info[0].get('expires_date')
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
            'product_id': product_id,
            'environment': environment,
            'original_transaction_id': original_transaction_id,
            'transaction_id': transaction_id,
            'expires_date': expires_date,
            'expiration_intent': expiration_intent,
            'in_app_ownership_type': in_app_ownership_type,
            'auto_renew_status': auto_renew_status,
            'original_purchase_date': transactionDate
        }
        response = purchase_details

    return response


@api_view(['POST'])
def AppStoreNotificationHandler(request):
    response = 501    
    if request.method == 'POST':
        envelope = json.loads(request.body)
        message = envelope["signedPayload"]
        apple_notify_iap(message)

    return Response(status.HTTP_200_OK)

def apple_notify_iap(message):
    response = 501
    decoded_header, decoded_payload, decoded_signature = decode_transaction(message)
    
    if decoded_payload:
        decoded_payload = json.loads(decoded_payload)
        notification_type = decoded_payload["notificationType"]
        bundle_id = decoded_payload["data"]["bundleId"]
        environment = decoded_payload["data"]["environment"]
        signed_transaction_info = decoded_payload["data"]["signedTransactionInfo"]
        signed_renewal_info = decoded_payload["data"]["signedRenewalInfo"]
        decoded_header_transaction_info, decoded_payload_transaction_info, decoded_signature_transaction_info = decode_transaction(signed_transaction_info)
        decoded_header_signed_renewal_info, decoded_payload_signed_renewal_info, decoded_signature_signed_renewal_info = decode_transaction(signed_renewal_info)

        if decoded_payload_transaction_info and decoded_payload_signed_renewal_info:
            decoded_payload_transaction_info = json.loads(decoded_payload_transaction_info)
            decoded_payload_signed_renewal_info = json.loads(decoded_payload_signed_renewal_info)
            message = ''
            response = verify_apple_pay(notification_type, bundle_id, environment, decoded_payload_transaction_info, decoded_payload_signed_renewal_info, decoded_signature, message)

    return response

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

