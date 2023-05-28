import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
import requests
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
import os
from course.models import Grade

from subscribe.models import GradePack, Product

User = get_user_model()


class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            is_staff=True,
            username='+23407048536974',
            email='testuser@example.com',
            password='password@123A'
        )
        self.user.is_staff = True

        self.data = {
            'email': 'imaraovie@gmail.com',
            'password': 'password@123A',
            'phone_number': '+23407048536974',

        }

    def test_BillingProduct_list_create_api_view(self):
        self.product = Product.objects.create(
            name='Monthly',
            product_id='com.edufox.sub.autorenew.monthly',
            amount='5500.00',
            currency="₦",
            duration=30,
            discount=None,
            platform="android",
        )
        self.product = Product.objects.create(
            name='Quarterly',
            product_id='com.edufox.sub.autorenew.quarterly',
            amount='12000.00',
            currency="₦",
            duration=90,
            discount=None,
            platform="android",
        )

        self.grade = Grade.objects.create(
            code='grade1',
            name='Grade 1',
            description='Grade 1'
        )

        self.grade = Grade.objects.create(
            code='grade2',
            name='Grade 2',
            description='Grade 2'
        )

        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        data = {
            'name': 'Yearly',
            'product_id': 'com.edufox.sub.autorenew.yearly',
            'platform': 'ios',
            "amount": '35000.00',
            "currency": "₦",
            "duration": 30,
            "discount": None,
            "platform": "android",
        }
        # print('GRADE: ', self.grade, type(self.grade))
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(
            reverse('subscribe:products-list'), data=data, format='json')
        # print('response', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # user = response.json()
        # self.assertEqual(user.get('user').get('email'), 'imaraovie@gmail.com')
        # self.assertEqual(user.get('user').get('username'), '+23407048536974')
        # self.assertEqual(user.get('grade'), 'Grade 1')

        # #test deletion of user
        # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(reverse('subscribe:products-list'))
        # print('GET PRODUCTS: ', response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verifyPurchase(self):
        purchase = {"autoRenewingAndroid": "true", "dataAndroid": "{\"orderId\":\"GPA.3339-5541-5514-80021\",\"packageName\":\"com.edufox\", \"productId\":\"com.edufox.sub.autorenew.monthly\",\"purchaseTime\":1682582797513,\"purchaseState\":0,\"purchaseToken\":\"mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg\",\"quantity\":1,\"autoRenewing\":true,\"acknowledged\":false}", "developerPayloadAndroid": "", "isAcknowledgedAndroid": "false", "obfuscatedAccountIdAndroid": "", "obfuscatedProfileIdAndroid": "", "packageNameAndroid": "com.edufox", "productId": "com.edufox.sub.autorenew.monthly", "purchaseStateAndroid": 1, "purchaseToken": "mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg",
                    "signatureAndroid": "HB5uDR4cFJPQh68gIZznypP5ZA1m7EMkbYgjvf3hTMvB2disrBmPUl+WFReukoFR14N21POyr8jfxID0aH5skl4PUNF0sfIMS6Ng/OCV0Vj08uUWrBIRSK8MuiU+fGVCjLVqXb/+Tr96gUSQo++Nl/AUEPOLEBxcdrAIozUPh/9Lw8SalkSvW6jgrbUo5Ym5MS3WLFHUaujyMRqX2KXrfHAl7roijL/BxNG+fSUVNpxfJF9ugE96SYSKNfsVufH98O6LNiZqeeykh4/iu2g1B4wmt+voBeHZ/wP3BRccX2yS4Bell7sgSjG4u65x2NObvllIemNPj222arJc1nsP8w==", "transactionDate": "1682582797513", "transactionId": "GPA.3339-5541-5514-80021", "transactionReceipt": "{\"orderId\":\"GPA.3339-5541-5514-80021\",\"packageName\":\"com.edufox\",\"productId\":\"com.edufox.sub.autorenew.monthly\",\"purchaseTime\":1682582797513,\"purchaseState\":0,\"purchaseToken\":\"mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg\",\"quantity\":1,\"autoRenewing\":true,\"acknowledged\":false}"}

        Product.objects.create(
            name='Monthly',
            product_id='com.edufox.sub.autorenew.monthly',
            amount='5500.00',
            currency="=N=",
            duration=30,
            discount=None,
            platform="ios",
        )
        Product.objects.create(
            name='Quarterly',
            product_id='com.edufox.sub.autorenew.quarterly',
            amount='12000.00',
            currency="=N=",
            duration=90,
            discount=None,
            platform="Android",
        )

        self.grade1 = Grade.objects.create(
            code='grade1',
            name='Grade 1',
            description='Grade 1'
        )

        self.grade2 = Grade.objects.create(
            code='grade2',
            name='Grade 2',
            description='Grade 2'
        )

        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        data = {
            "purchase-data": purchase,
            "is_sandbox": True,
            "grade": self.grade1.pk,
            "platform": "android"
        }
        # response = self.client.post(
        #     reverse('subscribe:verifyReceipt-list'), data=data, format='json')
        # print('verify_purchase_response1', response.json())
        # response = self.client.post(reverse('subscribe:verifyReceipt-list'), data=data, format='json')
        # print('verify_purchase_response2', response.json())

    def test_playstore_notify(self):
        data = {'message': {'data': 'eyJ2ZXJzaW9uIjoiMS4wIiwicGFja2FnZU5hbWUiOiJjb20uZWR1Zm94IiwiZXZlbnRUaW1lTWlsbGlzIjoiMTY4MjYwMTU5MjA3NiIsInN1YnNjcmlwdGlvbk5vdGlmaWNhdGlvbiI6eyJ2ZXJzaW9uIjoiMS4wIiwibm90aWZpY2F0aW9uVHlwZSI6MiwicHVyY2hhc2VUb2tlbiI6Im5tZWhpZGFnY2hrb2RrbmFiaHBpbmNrZC5BTy1KMU95RVZTXy1ac0xJNW9hUjFabGxEV2FqT3JpYTZZTWh2MTJYV3BBLThaX2tmVUNNa0ZNMUI0UTdrX0VUZTJ3WjgyNm1mekRQdS1zRlRraW94Qjd2ZjVxdW1TM2ktdyIsInN1YnNjcmlwdGlvbklkIjoiY29tLmVkdWZveC5zdWIuYXV0b3JlbmV3Lm1vbnRobHkifX0=',
                            'messageId': '7541642979606340', 'message_id': '7541642979606340', 'publishTime': '2023-04-27T13:19:52.269Z', 'publish_time': '2023-04-27T13:19:52.269Z'}, 'subscription': 'projects/edufox-services/subscriptions/eventarc-us-central1-trigger-2cpqm3oe-sub-255'}

        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # response = self.client.post(
        #     reverse('subscribe:playstorenotify-list'), data=data, format='json')
        # print('play_notify_response', response.json())

    # def test_subscribe(self):
    #     # host = "https://api-service-5wasy3cpxq-uc.a.run.app"
    #     host = "http://127.0.0.1:8000"
    #     login_url = f"{host}{reverse('api:login')}"

    #     response = requests.post(login_url, data={
    #         'username': '+2348023168805',
    #         'password': 'password@123A',
    #     })
    #     token = response.json()['auth_token']
    #     # print('login_url', token)
    #     url = f"{host}{reverse('subscribe:fetch-subscribe-detail')}"
    #     response = requests.get(url, headers={
    #         'Authorization': f"Token {token}",
    #         'Content-Type': 'application/json'
    #     })
    #     print('subscribe_response', response)

    def test_verify_purchase_ios(self):
        Product.objects.create(
            name='Monthly',
            product_id='com.edufox.sub.autorenew.monthly',
            amount='5500.00',
            currency="=N=",
            duration=30,
            discount=None,
            platform="ios",
        )
        GradePack.objects.create(
            label='KG',
            category="Nursery",
            range="1 - 3",
            description="Kg(nursery)1-3",
            grades=[
                1,
                2,
                3
            ],
        )
        data = {'purchase-data':
                {"transactionReceipt": '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',
                 "productId": 'com.edufox.sub.autorenew.monthly',
                 "transactionId": '2000000339335237',
                 "transactionDate": '1685286454000.0'},
                "is_sandbox": True,
                "grade": 1,
                "platform": 'ios'}

        productId = ""
        product = ""

        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })

        # print('token', response.json())
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        purchase_data = data.get('purchase-data')
        platform = data.get('platform')

        if purchase_data:
            productId = purchase_data.get('productId')

        products = Product.objects.filter(
            product_id=productId, platform=platform)
        if products.exists():
            product = products.first()

        response = self.client.post(
            reverse('subscribe:verifyReceipt-list'), data=data, format='json')
        response = response.json()
        # print("subscribe: ", response)

        self.assertEqual(purchase_data.get('transactionId'),
                         response.get('original_transaction_id'))
        self.assertEqual(product.pk, response.get('product'))

        # print('login_url', token)
        response = self.client.get(reverse('subscribe:fetch-subscribe-detail'), headers={
            'Authorization': f"Token {token}",
            'Content-Type': 'application/json'
        })
        response = response.json()
        print('subscribe_response', response)

        self.assertEqual(data.get('grade'), response[0].get(
            'grade') if response else None)
        self.assertEqual(product.pk, response[0].get(
            'product') if response else None)
