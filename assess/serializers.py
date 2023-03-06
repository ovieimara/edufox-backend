from datetime import datetime, timedelta
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import (Test, Assessment, Level)
from assess.models import  Test, Assessment
from subscribe.models import Subscribe
from djoser.serializers import UserSerializer


class TestSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    class Meta:
        model = Test
        fields = ['pk', 'question', 'options', 'valid_options', 'topic', "lesson", "subject", "grade", "level"]

    def get_options(self, obj):
        option1 = obj.option1
        option2 = obj.option2
        option3 = obj.option3
        option4 = obj.option4
        option5 = obj.option5
        option6 = obj.option6
        
        options = {
            "A" : option1,
            "B" : option2,
            "C" : option3,
            "D" : option4,
            "E" : option5,
            "F" : option6,
        }
        return options
    
    def create(self, validated_data):
        # print('validated_data: ', validated_data)
        request = self.context.get('request')
        question = validated_data['question']
        user = request.user
        if user.is_staff:
            instance = Test.objects.filter(question=question)
            if instance:
                return super().update(instance.first(), validated_data)
            
            return super().create(validated_data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    

class AssessmentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True, default={})
    # answer = serializers.MultipleChoiceField(choices=[])

    class Meta:
        model = Assessment
        fields = "__all__"

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print(kwargs)
    #     test = kwargs.get('test')
    #     instance = Test.objects.get(test=test)
    #     if instance:
    #         choices = [('A', instance.option1), ('B', instance.option2), ('C', instance.option3), ('D', instance.option4), ('E', instance.option5), ('F', instance.option6)]
    #         self.fields['answer'].choices = choices

    def get_status(self, obj):
        valid_options = obj.test.valid_options
        answer = obj.answer
        result = [0] * len(valid_options)

        # for i in range(len(answer.keys())):
        #     ans = list(answer.keys())[i]
        #     for j in range(len(valid_options)):
        #         valid = valid_options[j]
        #         if ans != valid:
        #             return False
                
        #         result[i] = 1

        for i in range(len(answer.keys())):
            ans = list(answer.keys())[i]
            for j in range(len(valid_options.keys())):
                valid = list(valid_options.keys())[j]
                if ans != valid:
                    return False
                
                result[i] = 1

        return all(result)
    
    def create(self, validated_data):
        # print('validated_data: ', validated_data)
        request = self.context.get('request')
        test = validated_data['test']
        user = request.user
        if user:
            tests = user.assessments.filter(test=test)
            if tests.exists():
                return super().update(tests.first(), validated_data)
            
            validated_data['user'] = user
            return super().create(validated_data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
                

class LevelSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Level
        fields = "__all__"


