from django.test import TestCase

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Grade, Subject, Lecturer

User = get_user_model()

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_create_grade(self):
        Grade.objects.create(
            code='grade1', 
            name='Grade 1', 
            description='Grade 1'
        )
        grade = Grade.objects.get(name='Grade 1')
        self.assertEqual(grade.name, 'Grade 1')
        self.assertEqual(grade.code, 'grade1')



    def test_create_subject(self):
        Subject.objects.create(
            code='phy101', 
            name='Physics', 
            description='Physics',
        )
        grade = Subject.objects.get(name='Physics')
        self.assertEqual(grade.name, 'Physics')
        self.assertEqual(grade.code, 'phy101')

    def test_create_lecturer(self):
        Lecturer.objects.create(
            first_name='ovie', 
            last_name='imara', 
        )
        lecturer = Lecturer.objects.get(first_name='ovie')
        self.assertEqual(lecturer.first_name, 'ovie')
        self.assertEqual(lecturer.last_name, 'imara')