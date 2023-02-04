# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase

# User = get_user_model()

# class SignInTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser', 
#             email='testuser@example.com', 
#             password='password@123'
#         )

#         # print('USER', dir(self.user))

#     def test_sign_in(self):
#         url = '/api/v1/token/login/'
#         data = {
#             'username': 'testuser',
#             'password': 'password@123'
#         }

#         response = self.client.post(reverse('login'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('auth_token', response.data)

#     def test_logout(self):
#         # Log in the user
#         response = self.client.post(reverse('login'), data={
#             'username': 'testuser',
#             'password': 'password@123',
#         })
#         # print('response', response.json())
#         self.assertEqual(response.status_code, 200)
#         token = response.json()['auth_token']
        
        
#         # Log out the user
#         self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
#         response = self.client.post(reverse('logout'), content_type='application/json')
#         self.assertEqual(response.status_code, 204)


#     def test_update_user(self):
#         # retrieve the URL for the view
#         # url = reverse('user-update', kwargs={'username': 'testuser'})

#         # update the user
#         data = {
#             'username': 'testuser',
#             'phone_number': '1234567890'
#         }
#         url = f"/api/v1/students/{data['username']}"

#         # self.client.login(username='testuser', password='password@123')
#         response = self.client.put(url, data, format='json')
#         print('update', response)

#         # check the response
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['username'], 'testuser')
#         self.assertEqual(response.data['phone_number'], '1234567890')


#     # def test_activate(self):
#     #     # url = '/api/v1/token/login/'
#     #     data = {
#     #         'username': 'testuser',
#     #         'password': 'password@123'
#     #     }

#     #     response = self.client.post(reverse('login'), data, format='json')
#     #     auth_token = response.json()['auth_token']
#     #     activation_url = reverse('activate', kwargs={'uid': self.user.uid, 'token': auth_token})
#     #     activation_url = f'/api/v1/activate/{self.user.id}/{auth_token}'
#     #     print('activation_url', activation_url)
#     #     response = self.client.post(activation_url)
#     #     print(response)
#     #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#     #     self.user.refresh_from_db()
#     #     self.assertTrue(self.user.is_active)