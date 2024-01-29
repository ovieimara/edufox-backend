from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime
from platform import platform
from typing import Any, Dict, List, Tuple
from venv import create
from django.http import HttpRequest
import requests

from rsa import verify
from course.models import Video
# from edufox.constants import FLUTTERWAVE_WEB, IOS
from rest_framework import status
from edufox.views import printOutLogs, update_user_data
from subscribe.models import GradePack, InAppPayment, Product, Subscribe
from django.utils import timezone
from django.db.models import Q
from enum import Enum

from subscribe.serializers import InAppPaymentSerializer, SubscribeSerializer


class Platform(Enum):
    IOS = 'ios'
    ANDROID = 'android'
    WEB = 'web'
    FLUTTERWAVE_WEB = 'flutterwave_web'


class UserSubscriptionABC(ABC):
    def __init__(self, user: str, video_id: str = '') -> None:
        self.user = user
        self.video_id = video_id

    @abstractmethod
    def get_user_subscriptions(self):
        """ fetch subscriptions that are valid after timezone.now"""

    @abstractmethod
    def isValidSubForVideo(self) -> bool:
        """check if subscription is valid for a video"""

    @abstractmethod
    def get_all_user_subscriptions(self):
        """return all subscriptions for this user"""


class MySubscription(UserSubscriptionABC):

    def get_user_subscriptions(self):
        return self.user.subscriptions_user.filter(Q(payment_method__expires_date__gt=timezone.now())).order_by("-created")

    def get_all_user_subscriptions(self):
        # print('subscriptions: ', self.user.subscriptions_user)
        queryset = Subscribe.objects.all()

        query = queryset.filter(payment_method__expires_date__gt=timezone.now(
        ), user=self.user).order_by("-created") if self.user.is_authenticated else []
        print("queryset: ", query)

        return query

    def get_video_grades(self) -> list:
        video_grades = {}
        try:
            video_queryset = Video.objects.filter(video_id=self.video_id)
            if video_queryset.exists():
                video_obj = video_queryset.first()
                grades = video_obj.grade.all()
                video_grades = {grade.pk for grade in grades}
        except Exception as ex:
            print('video object error: ', ex)

        return video_grades

    def isValidSubForVideo(self) -> bool:
        subscriptions = self.get_all_user_subscriptions()
        if subscriptions:
            video_grades = self.get_video_grades()
            for sub in subscriptions.all():
                subscription_grades = set(sub.grade.grades)
                grades_intersection = subscription_grades & video_grades
                print(grades_intersection, subscription_grades, video_grades)

                if grades_intersection:
                    return True
        return False

        # subscriptions = subscriptions.objects.filter(
        #     grade__grades__contains=values)
        # print("subscriptions: ", subscriptions.all(),
        #       self.get_video_grades(), type(self.get_video_grades()))

        # if subscriptions.exists():
        # subscription_obj = subscriptions.filter(
        #     # Q(grade__grades__contains=self.get_video_grades()) &
        #     Q(
        #         payment_method__expires_date__gt=timezone.now())
        # )
        # print("subscriptions2: ", subscription_obj)
        # if subscription_obj.exists():
        # return True


class DateConvert(ABC):
    '''Super class to handle date conversion'''

    @abstractmethod
    def convert(self, ms_date_time):
        '''convert date from ms to datetime'''


class PosixToDatetime(DateConvert):

    def convert(self, ms_date_time) -> datetime:
        transactionDate = ''
        if ms_date_time:
            transactionDate = datetime.datetime.fromtimestamp(
                float(ms_date_time)/1000.0)

        return transactionDate


class PaymentHandler(ABC):
    '''Super class to handle App Subscriber Payment'''
    # @abstractmethod
    # def process_request_data(self):
    #     '''get purchase request data'''

    @abstractmethod
    def verify_purchase(self) -> requests.Response:
        '''verify purchase'''

    @abstractmethod
    def process_purchase_data(self, receipt_json_data: Dict, conversion_fn: DateConvert) -> Dict:
        '''get purchase data'''

    def subscribe(self):
        '''create subscription'''

    @abstractmethod
    def process_subscription(self) -> Dict:
        '''process subscription'''


# class StoreNotification(ABC):
#     '''Super class to handle App Subscriber Payment'''

@dataclass
class AppstorePaymentHandler(PaymentHandler):
    # request: HttpRequest = None
    receipt_data: Dict = field(default_factory=Dict)
    is_sandbox: bool = True
    grade: int = None
    user: Any = None
    platform: str = ''

    def __post_init__(self):
        self.endpoint_url = 'https://buy.itunes.apple.com/verifyReceipt' if not self.is_sandbox else 'https://sandbox.itunes.apple.com/verifyReceipt'

    def verify_purchase(self) -> requests.Response:
        try:
            data = {"receipt-data": self.receipt_data,
                    "password": '7f64d85b4b2046e6b0e2499e512d6c31'}
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            return requests.post(self.endpoint_url, json=data, headers=headers)
        except Exception as ex:
            printOutLogs(
                'Appstore Receipt Verification exception occurred: ', ex)
        return None

    def check_response(self, response: requests.Response) -> Tuple[Dict, int]:
        if response and response.status_code != 200:
            return response.json(), response.status_code

        response_json: Dict = response.json() if response else Dict

        # If the response status is not 0, the receipt is invalid
        if not response_json or response_json.get('status') != 0:
            return response_json, status.HTTP_400_BAD_REQUEST

        return response_json, status.HTTP_200_OK

    def process_purchase_data(self, receipt_json_data: Dict, conversion_fn: DateConvert,
                              gateway: str) -> Dict:
        purchase_data = {}
        if receipt_json_data:
            environment = receipt_json_data.get('environment')
            latest_receipt_info = receipt_json_data.get(
                'latest_receipt_info', {})
            pending_renewal_info = receipt_json_data.get(
                'pending_renewal_info', {})

            if len(latest_receipt_info) > 0:
                original_transaction_id = latest_receipt_info[0].get(
                    'original_transaction_id')
                transaction_id = latest_receipt_info[0].get('transaction_id')
                posix_date_time = latest_receipt_info[0].get(
                    'purchase_date_ms')
                expires_date = latest_receipt_info[0].get('expires_date_ms')

            else:
                inapp = receipt_json_data.get('in_app', {})
                if inapp:
                    transaction_id = inapp[0].get('transaction_id')
                    posix_date_time = inapp[0].get('purchase_date_ms')
                    original_transaction_id = inapp[0].get(
                        'original_transaction_id')
                    in_app_ownership_type = inapp[0].get(
                        'in_app_ownership_type')

            if pending_renewal_info:
                original_transaction_id2 = pending_renewal_info[0].get(
                    'original_transaction_id')
                auto_renew_status = pending_renewal_info[0].get(
                    'auto_renew_status')
                expiration_intent = pending_renewal_info[0].get(
                    'expiration_intent')

            if not original_transaction_id and original_transaction_id2:
                original_transaction_id = original_transaction_id2

            if posix_date_time:
                transactionDate = datetime.datetime.fromtimestamp(
                    float(posix_date_time)/1000.0)

            purchase_data = {
                'name': gateway,
                'environment': environment if environment else '',
                'original_transaction_id': original_transaction_id if original_transaction_id else '',
                'transaction_id': transaction_id if transaction_id else '',
                'expires_date': conversion_fn(expires_date),
                'expiration_intent': expiration_intent if expiration_intent else '',
                'in_app_ownership_type': in_app_ownership_type if in_app_ownership_type else '',
                'auto_renew_status': auto_renew_status if auto_renew_status else '',
                'original_purchase_date': transactionDate if transactionDate else ''
            }

        return purchase_data

    def create_product(self, model: Product) -> Product:

        product: model = model.objects.none()

        try:
            product_queryset = model.objects.filter(
                product_id=self.product_id.strip(), platform=self.platform.strip())

            if product_queryset.exists():
                product = product_queryset.first()

        except model.DoesNotExist as ex:
            print(f'payment_serializer exception occurred: {ex}')

        return product

    def createPayment(self, payment_data: Dict, product: Product,  in_app_payment_serializer: InAppPaymentSerializer) -> Tuple[Dict, InAppPayment]:
        if not payment_data:
            return {}, None

        try:
            in_app_payment_serializer = in_app_payment_serializer(
                data=payment_data)
            in_app_payment_serializer.is_valid(raise_exception=True)
            in_app_payment_obj = in_app_payment_serializer.save(
                product=product, user=self.user)

            in_aap_payment_data = {}
            if in_app_payment_serializer:
                in_aap_payment_data = in_app_payment_serializer.data

            return in_aap_payment_data, in_app_payment_obj

        except Exception as ex:
            print(f'InAppPayment exception occurred: {ex}')

        return {}, None

    def processGradePack(self) -> GradePack:
        grade_pack = GradePack.objects.none()

        try:
            grade_pack_queryset = GradePack.objects.all().filter(pk=self.grade)
            if grade_pack_queryset.exists():
                grade_pack = grade_pack_queryset.first()
        except Exception as ex:
            print(f'Grade exception occurred: {ex}')

        return grade_pack

    def createSubscription(self, product: Product, payment: InAppPayment, grade: GradePack) -> Dict:
        try:
            initialize_data = {
                "user": None,
                "product": None,
                "payment_method": None,
                "grade": None
            }

            subscribe_serializer = SubscribeSerializer(data=initialize_data)
            subscribe_serializer.is_valid(raise_exception=True)
            subscribe_serializer.save(
                user=self.user, product=product, payment_method=payment, grade=grade)
            if subscribe_serializer:
                return subscribe_serializer.data

        except Exception as ex:
            # print(f'SubscribeSerializer exception occurred: {ex}')
            printOutLogs('SubscribeSerializer exception occurred: ', ex)

        return {}

    def finalize(self, resp: Dict, response_json: Dict, serializer_data: Dict) -> Tuple[Dict, int]:
        state = status.HTTP_400_BAD_REQUEST
        resp = {}

        resp['status'] = response_json.get('status')
        state = status.HTTP_200_OK

        update_user_data()  # update cache

        if serializer_data:
            state = status.HTTP_201_CREATED

        return resp, state

    def process_subscription(self, response: requests.Response, conversion_fn, in_app_payment_serializer: InAppPaymentSerializer, product: Product) -> Tuple[Dict, int]:
        response = self.verify_purchase()
        response_json, state = self.check_response(response)
        if state != status.HTTP_200_OK:
            return response_json, state

        payment_data = self.process_purchase_data(
            response_json, conversion_fn, 'Apple In-App')
        product = self.create_product(product)
        in_app_payment_data, in_app_payment_obj = self.createPayment(
            payment_data, product, in_app_payment_serializer)

        grade_pack_obj = self.processGradePack()
        serializer_data = self.createSubscription(
            product, in_app_payment_obj, grade_pack_obj)
        resp, state = self.finalize(
            in_app_payment_data, response_json, serializer_data)

        return resp, state
