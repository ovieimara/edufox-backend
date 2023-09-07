from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .validators import validate_username
from djoser.serializers import UserSerializer
from .models import (Earn, Referral, Student, TempStudent, Country)
from course.models import Grade
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


# User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    # student_id = serializers.CharField(default="")
    # first_name = serializers.CharField()
    # last_name = serializers.CharField()
    # phone_number = serializers.CharField(default="")

    class_grade = serializers.SerializerMethodField()
    age = serializers.IntegerField(default=0)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    user = UserSerializer(default={})
    my_referral = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(
        choices=['male', 'female'], allow_null=True, allow_blank=True, default='')
    # image_url = serializers.CharField(default="")
    # name_institution = serializers.CharField(allow_null=True, default="")
    # email = serializers.EmailField()
    # password = serializers.CharField(allow_null=False)

    # email = serializers.EmailField(validators=[unique_user_email])

    class Meta:
        model = Student
        # fields = "__all__"

        fields = ['pk', 'dob', 'phone_number', 'grade', 'age',
                  'gender', 'image_url', 'name_institution', 'user', 'class_grade', "referral", 'my_referral', 'earning', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True},
                        'user': {'read_only': True}
                        }

    def get_my_referral(self, obj):
        return obj.my_referral_code

    def get_class_grade(self, obj):
        if obj and obj.grade:
            return obj.grade.name

        return ''

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        # user = get_object_or_404(User, username=phone_number)
        user = None
        try:
            user = User.objects.get(username=phone_number)
        except User.DoesNotExist as ex:
            print(ex)

        if user:
            validated_data['user'] = user
        return super().create(validated_data)

    # def validate_dob(self, value):
    #     return datetime.strptime(value, '%d-%m-%Y').date()

    # def update(self, instance, validated_data):
    #     grade = validated_data.get('grade')
    #     grade_instance = get_object_or_404(Grade, name=grade)
    #     print(grade, grade_instance)
    #     if grade_instance:
    #         validated_data['grade'] = grade_instance
    #     return super().update(instance, validated_data)


class TempStudentSerializer(serializers.ModelSerializer):
    # student_id = serializers.CharField(default="")
    first_name = serializers.CharField(default="")
    last_name = serializers.CharField(default="")
    # username = serializers.CharField()
    email = serializers.EmailField(default="")
    phone_number = serializers.CharField(
        max_length=15, allow_blank=False, trim_whitespace=True, default="")
    # grade = serializers.ChoiceField(choices=['KG 1', 'KG 2', 'KG 3', 'KG 4', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6', 'JSS 1', 'JSS 2', 'JSS 3', 'SSS 1', 'SSS 2', 'SSS 3'])
    age = serializers.IntegerField(default=0)
    gender = serializers.ChoiceField(
        choices=['male', 'female'], allow_blank=True, allow_null=True, default=dict)
    # image_url = serializers.CharField(default="")
    name_institution = serializers.CharField(default="")
    # otp_code = serializers.SerializerMethodField()

    # email = serializers.EmailField(validators=[unique_user_email])

    class Meta:
        model = TempStudent
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True},
                        'user': {'read_only': True}}

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        country = attrs.get('country')
        obj = get_object_or_404(Country, name__iexact=country.name)
        attrs['username'] = obj.code + phone_number
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email',
                  'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class ReferralSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=['active', 'inactive'], allow_null=True, allow_blank=True, default='')
    code = serializers.CharField(max_length=255, allow_blank=True, validators=[
        UniqueValidator(queryset=Referral.objects.all())])

    class Meta:
        model = Referral
        fields = "__all__"


class EarnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earn
        fields = "__all__"
