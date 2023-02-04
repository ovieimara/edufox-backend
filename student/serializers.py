from django.contrib.auth import get_user_model
from rest_framework import serializers
from .validators import validate_username
from djoser.serializers import UserSerializer
from .models import Student, TempStudent

User = get_user_model()

class StudentSerializer(serializers.ModelSerializer):
    # student_id = serializers.CharField(default="")
    # first_name = serializers.CharField()
    # last_name = serializers.CharField()
    phone_number = serializers.CharField(default="")
    grade = serializers.ChoiceField(choices=['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6'], default='')
    age = serializers.IntegerField(default=0)
    user = UserSerializer(default={})
    gender = serializers.ChoiceField(choices=['male', 'female'], default='')
    image_url = serializers.CharField(default="")
    name_institution = serializers.CharField(default="")
    # email = serializers.EmailField()

    # email = serializers.EmailField(validators=[unique_user_email])


    class Meta:
        model = Student
        # fields = "__all__"

        fields = ['phone_number', 'grade', 'age', 'gender', 'image_url', 'name_institution', 'user']
        extra_kwargs = {'password': {'write_only': True},
        'user': {'read_only': True}}

    # def create(self, validated_data):
    #     user_name = validated_data.get('username')
    #     if not user_name:
    #         validated_data['username'] = validated_data['first_name']
    #     return super().create(validated_data)

class TempStudentSerializer(serializers.ModelSerializer):
    # student_id = serializers.CharField(default="")
    first_name = serializers.CharField(default="")
    last_name = serializers.CharField(default="")
    username = serializers.CharField(default="")
    email = serializers.EmailField(default="")
    phone_number = serializers.CharField(default="")
    grade = serializers.ChoiceField(choices=['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6'], default='')
    age = serializers.IntegerField(default=0)
    gender = serializers.ChoiceField(choices=['male', 'female'], default='')
    image_url = serializers.CharField(default="")
    name_institution = serializers.CharField(default="")

    # email = serializers.EmailField(validators=[unique_user_email])

    class Meta:
        model = TempStudent
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True},
        'user': {'read_only': True}}