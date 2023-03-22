from datetime import datetime, timedelta
from rest_framework import serializers
from .models import (Grade, Comment, Rate, Seek, Subject, Lecturer, Video, Interaction, 
InteractionType, Resolution, Seek)
# from assess.models import  Test, Assessment
from subscribe.models import Subscribe

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = '__all__'
        # depth = 1

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user:
            subscriptions = request.user.subscriptions_user.all()
            if subscriptions.exists():
                subscribed = subscriptions.filter(grade=obj.grade).first()
                if subscribed:
                    return subscribed.is_valid(datetime.now())
                return False
            return False
        return False

class InteractionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionType
        fields = "__all__"

class InteractionSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=['END', 'EXIT', 'PAUSE','PLAY', 'START', 'STOP'])
    class Meta:
        model = Interaction
        fields = "__all__"

class SeekSerializer(serializers.ModelSerializer):
    direction = serializers.ChoiceField(choices=['FW', 'RW'])
    class Meta:
        model = Seek
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        # print('USER: ', user)
        if user and not user.is_anonymous:
            validated_data['user'] = request.user
            return super().create(validated_data)
        return validated_data

# class AssessmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Assessment
#         fields = "__all__"


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = "__all__"