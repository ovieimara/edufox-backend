import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
import os
from course.models import Grade

from subscribe.models import Product

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
        self.user.is_staff=True

        self.data = {
            'email': 'imaraovie@gmail.com',
            'password': 'password@123A',
            'phone_number' : '+23407048536974',

        }

    def test_BillingProduct_list_create_api_view(self):
        print(reverse('students-list'))
        
        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        data = {
            'name' : 'monthly',
            'product_id': 'monthly',
            'platform': 'ios'
        }
        # print('GRADE: ', self.grade, type(self.grade))
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(reverse('subscribe:products-list'), data=data, format='json')
        print('response', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # user = response.json()
        # self.assertEqual(user.get('user').get('email'), 'imaraovie@gmail.com')
        # self.assertEqual(user.get('user').get('username'), '+23407048536974')
        # self.assertEqual(user.get('grade'), 'Grade 1')

        # #test deletion of user
        # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(reverse('subscribe:products-list'))
        print('GET PRODUCTS: ', response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    


    def test_verifyPurchase(self):
        purchase = {"autoRenewingAndroid": "true", "dataAndroid": "{\"orderId\":\"GPA.3339-5541-5514-80021\",\"packageName\":\"com.edufox\", \"productId\":\"com.edufox.sub.autorenew.monthly\",\"purchaseTime\":1682582797513,\"purchaseState\":0,\"purchaseToken\":\"mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg\",\"quantity\":1,\"autoRenewing\":true,\"acknowledged\":false}", "developerPayloadAndroid": "", "isAcknowledgedAndroid": "false", "obfuscatedAccountIdAndroid": "", "obfuscatedProfileIdAndroid": "", "packageNameAndroid": "com.edufox", "productId": "com.edufox.sub.autorenew.monthly", "purchaseStateAndroid": 1, "purchaseToken": "mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg", "signatureAndroid": "HB5uDR4cFJPQh68gIZznypP5ZA1m7EMkbYgjvf3hTMvB2disrBmPUl+WFReukoFR14N21POyr8jfxID0aH5skl4PUNF0sfIMS6Ng/OCV0Vj08uUWrBIRSK8MuiU+fGVCjLVqXb/+Tr96gUSQo++Nl/AUEPOLEBxcdrAIozUPh/9Lw8SalkSvW6jgrbUo5Ym5MS3WLFHUaujyMRqX2KXrfHAl7roijL/BxNG+fSUVNpxfJF9ugE96SYSKNfsVufH98O6LNiZqeeykh4/iu2g1B4wmt+voBeHZ/wP3BRccX2yS4Bell7sgSjG4u65x2NObvllIemNPj222arJc1nsP8w==", "transactionDate": "1682582797513", "transactionId": "GPA.3339-5541-5514-80021", "transactionReceipt": "{\"orderId\":\"GPA.3339-5541-5514-80021\",\"packageName\":\"com.edufox\",\"productId\":\"com.edufox.sub.autorenew.monthly\",\"purchaseTime\":1682582797513,\"purchaseState\":0,\"purchaseToken\":\"mdkdphoffdgljgpnihkafaon.AO-J1OyK6BjhDdHIvHJMgq_spohu_Z0Tlkb8MaJmVsIrM2MazO6vfrXOV5z8G8C6FNmSdoNmi2c_xT6k9_DSQWq0e-VO8i8Ddg\",\"quantity\":1,\"autoRenewing\":true,\"acknowledged\":false}"}

        product = Product.objects.create(
            name = 'Monthly',
            product_id = 'com.edufox.sub.autorenew.monthly',
            amount = '5500.00',
            currency = "=N=",
            duration = 30,
            discount = None,
            platform = "Android",
        )

        Product.objects.create(
            name = 'Quarterly',
            product_id = 'com.edufox.sub.autorenew.quarterly',
            amount = '12000.00',
            currency = "=N=",
            duration = 90,
            discount = None,
            platform = "Android",
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
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        data = {
            "purchase-data": purchase, 
            "is_sandbox" : True,
            "grade" : 2,
            "platform": "android"
        }
        response = self.client.post(reverse('subscribe:verifyReceipt-list'), data=data, format='json')
        print('verify_purchase_response', response.json())


    def test_playstore_notify(self):
        data = {'message': {'data': 'eyJ2ZXJzaW9uIjoiMS4wIiwicGFja2FnZU5hbWUiOiJjb20uZWR1Zm94IiwiZXZlbnRUaW1lTWlsbGlzIjoiMTY4MjYwMTU5MjA3NiIsInN1YnNjcmlwdGlvbk5vdGlmaWNhdGlvbiI6eyJ2ZXJzaW9uIjoiMS4wIiwibm90aWZpY2F0aW9uVHlwZSI6MiwicHVyY2hhc2VUb2tlbiI6Im5tZWhpZGFnY2hrb2RrbmFiaHBpbmNrZC5BTy1KMU95RVZTXy1ac0xJNW9hUjFabGxEV2FqT3JpYTZZTWh2MTJYV3BBLThaX2tmVUNNa0ZNMUI0UTdrX0VUZTJ3WjgyNm1mekRQdS1zRlRraW94Qjd2ZjVxdW1TM2ktdyIsInN1YnNjcmlwdGlvbklkIjoiY29tLmVkdWZveC5zdWIuYXV0b3JlbmV3Lm1vbnRobHkifX0=', 'messageId': '7541642979606340', 'message_id': '7541642979606340', 'publishTime': '2023-04-27T13:19:52.269Z', 'publish_time': '2023-04-27T13:19:52.269Z'}, 'subscription': 'projects/edufox-services/subscriptions/eventarc-us-central1-trigger-2cpqm3oe-sub-255'}

        response = self.client.post(reverse('api:login'), data={
            'username': '+23407048536974',
            'password': 'password@123A',
        })
        token = response.json()['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.post(reverse('subscribe:playstorenotify-list'), data=data, format='json')
        print('play_notify_response', response.json())