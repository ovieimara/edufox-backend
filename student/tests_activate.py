# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model
# User = get_user_model()


# class ActivationTestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='test_user', email='test@example.com', password='password')
#         self.activation_url = reverse('djoser:activate', kwargs={'uid': self.user.id, 'token': self.user.signup_token})

#     def test_activate(self):
#         response = self.client.post(self.activation_url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.is_active)

