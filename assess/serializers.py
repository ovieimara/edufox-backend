from datetime import datetime, timedelta
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import (Test, Assessment, Level)
from assess.models import  Test, Assessment
from subscribe.models import Subscribe
from djoser.serializers import UserSerializer
from collections import Counter


class TestSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(read_only=True, default=list)
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
        fields = ['pk', 'question', 'valid_answers', 'options', 'answers', 'topic', "lesson", "subject", "grade", "level", "option1", "option2", "option3", "option4", "option5", "option6"]
        # depth = 2


    # def get_options(self, obj):
    #     option1 = obj.option1
    #     option2 = obj.option2
    #     option3 = obj.option3
    #     option4 = obj.option4
    #     option5 = obj.option5
    #     option6 = obj.option6
        
    #     options = {
    #         "A" : option1,
    #         "B" : option2,
    #         "C" : option3,
    #         "D" : option4,
    #         "E" : option5,
    #         "F" : option6,
    #     }
    #     return options
    
    def capitalise(self, value):
        return value.capitalize() if value else value
    
    def create(self, validated_data):
        
        request = self.context.get('request')
        question = validated_data.get('question') if validated_data else ''
        valid_answers = validated_data.pop('answers') if validated_data else ''

        options = [self.capitalise(validated_data.pop(f'option{i}')) for i in range(1, 7) if validated_data]    

        valid_answers_arr = valid_answers.split(',') if valid_answers else None
        valid_answers = [int(option.strip()) - 1 for option in valid_answers_arr if option and option.strip().isdigit()]  

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

        options = [self.capitalise(validated_data.pop(f'option{i}')) for i in range(1, 7) if validated_data]           

        valid_answers_arr = valid_answers.split(',') if valid_answers else None
        valid_answers = [int(option.strip()) - 1 for option in valid_answers_arr if option and option.strip().isdigit()]  

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


