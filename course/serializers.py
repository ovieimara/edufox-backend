from datetime import datetime, timedelta
from rest_framework import serializers
from .models import (Grade, Comment, Rate, Subject, Lecturer, Video, Interaction, 
InteractionType, Resolution)
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
        if request.user:
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
    class Meta:
        model = Interaction
        fields = "__all__"

# class TestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Test
#         fields = "__all__"

# class AssessmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Assessment
#         fields = "__all__"


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = "__all__"