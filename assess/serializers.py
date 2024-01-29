from datetime import datetime, timedelta
from venv import create
from rest_framework import serializers, status
from rest_framework.fields import empty
from rest_framework.response import Response

from course.models import Grade, Lesson, Subject, Topic
from .models import (Test, Assessment, Level)
from assess.models import Test, Assessment
from subscribe.models import Subscribe
from djoser.serializers import UserSerializer
from collections import Counter
from django.utils.html import escape


class TestSerializer(serializers.ModelSerializer):
    # options = serializers.JSONField(default=list)
    options = serializers.SerializerMethodField()
    valid_answers = serializers.JSONField(read_only=True, default=list)
    answers = serializers.CharField(max_length=15, write_only=True)
    option1 = serializers.CharField(default='', write_only=True)
    option2 = serializers.CharField(default='', write_only=True)
    option3 = serializers.CharField(default='', write_only=True)
    option4 = serializers.CharField(default='', write_only=True)
    option5 = serializers.CharField(default='', write_only=True)
    option6 = serializers.CharField(default='', write_only=True)

    class Meta:
        model = Test
        fields = ['pk', 'question', 'valid_answers', 'options', 'answers', 'topic', "lesson",
                  "subject", "grade", "level", "option1", "option2", "option3", "option4", "option5", "option6"]
        # depth = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.order_by(
            'title')  # Sort topics by title
        self.fields['lesson'].queryset = Lesson.objects.order_by(
            'title')  # Sort lesson by title
        self.fields['subject'].queryset = Subject.objects.order_by(
            'name')  # Sort subjects by title
        self.fields['grade'].queryset = Grade.objects.order_by(
            'pk')  # Sort subjects by title

    def get_options(self, obj):
        return [option for option in obj.options if option]
        # option1 = obj.option1
        # option2 = obj.option2
        # option3 = obj.option3
        # option4 = obj.option4
        # option5 = obj.option5
        # option6 = obj.option6

        # options = {
        #     "A" : option1,
        #     "B" : option2,
        #     "C" : option3,
        #     "D" : option4,
        #     "E" : option5,
        #     "F" : option6,
        # }
        # return options

    def capitalise(self, value):
        return escape(value).capitalize() if value else value

    def strip_value(self, value):
        return int(escape(value.strip(
        ))) if value else value

    # def __init__(self, instance=None, data=..., **kwargs):
    #     super().__init__(instance, data, **kwargs)
    def create_options(self, validated_data: dict) -> list:
        options = []
        for i in range(1, 10):
            val = validated_data.pop(f'option{i}', '')
            if val:
                options.append(self.capitalise(val))
        return options

        # return [self.capitalise(validated_data.pop(
        #     f'option{i}')) for i in range(1, 7) if validated_data.get(f'option{i}')]

    def create(self, validated_data):
        request = self.context.get('request')
        question = validated_data.get('question') if validated_data else ''
        valid_answers = validated_data.pop('answers') if validated_data else ''
        topic = validated_data.get('topic')
        lesson = validated_data.get('lesson')
        print("lesson: ", lesson.title)

        if question:
            question = escape(question)

        if not topic and lesson:
            lesson_queryset = Lesson.objects.filter(title=lesson)
            if lesson_queryset.exists():
                validated_data['topic'] = lesson_queryset.first().topic

        # iterate thru option1 - 6
        options = self.create_options(validated_data)
        # options = [self.capitalise(validated_data.pop(
        #     f'option{i}')) for i in range(1, 7) if validated_data.get(f'option{i}')]

        valid_answers_arr = valid_answers.split(',') if valid_answers else None
        valid_answers = [self.strip_value(
            option) - 1 for option in valid_answers_arr if option and option.strip().isdigit()]

        validated_data['options'] = options
        validated_data['valid_answers'] = valid_answers

        user = request.user
        if user.is_staff:
            instance = Test.objects.filter(question=question)
            if instance:
                return super().update(instance.first(), validated_data)

            return super().create(validated_data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        valid_answers = validated_data.pop('answers') if validated_data else ''

        options = self.create_options(validated_data)

        # options = [self.capitalise(validated_data.pop(
        #     f'option{i}')) for i in range(1, 7) if validated_data.get(
        #     f'option{i}')]

        valid_answers_arr = valid_answers.split(',') if valid_answers else None
        valid_answers = [self.strip_value(
            option) - 1 for option in valid_answers_arr if option and option.strip().isdigit()]

        validated_data['options'] = options
        validated_data['valid_answers'] = valid_answers
        user = request.user
        if user.is_staff:
            return super().update(instance, validated_data)

        return Response(status=status.HTTP_401_UNAUTHORIZED)


class AssessmentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True, default=None)
    # answer = serializers.MultipleChoiceField(choices=[])

    class Meta:
        model = Assessment
        fields = "__all__"

    def get_status(self, obj):
        valid_answers = obj.test.valid_answers
        answers = obj.answer
        # print('OBJ: ', obj.test.valid_answers, answers)

        return self.compareAnswers(valid_answers, answers)

    def compareAnswers(self, valid_answers=None, answers=None):
        if not valid_answers:
            valid_answers = []
        if not answers:
            answers = []

        if not valid_answers and not answers:
            return []

        result = [False] * len(answers)
        valid_answers_dict = Counter(valid_answers)
        for index, answer in enumerate(answers):
            if valid_answers_dict.get(answer):
                valid_answers_dict[answer] -= 1
                result[index] = True

        return result

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print(kwargs)
    #     test = kwargs.get('test')
    #     instance = Test.objects.get(test=test)
    #     if instance:
    #         choices = [('A', instance.option1), ('B', instance.option2), ('C', instance.option3), ('D', instance.option4), ('E', instance.option5), ('F', instance.option6)]
    #         self.fields['answer'].choices = choices

    # def get_status(self, obj):
    #     valid_options = obj.test.valid_answers
    #     answer = obj.answer
    #     result = [0] * len(valid_options)

    #     for i in range(len(answer.keys())):
    #         ans = list(answer.keys())[i]
    #         for j in range(len(valid_options.keys())):
    #             valid = list(valid_options.keys())[j]
    #             if ans != valid:
    #                 return False

    #             result[i] = 1

    #     return all(result)

    def create(self, validated_data):
        request = self.context.get('request')
        # print('validated_data: ', request.user)
        test = validated_data['test']
        user = request.user if request.user else None
        if user:
            tests = user.assessments.filter(test=test)
            validated_data['user'] = user

            if tests.exists():
                return super().update(tests.first(), validated_data)

            return super().create(validated_data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"
