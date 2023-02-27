from datetime import datetime
from rest_framework import serializers
from .models import (Grade, Comment, Rate, Subject, Lecturer, Video, Interaction, 
InteractionType, Test, Assessment)
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
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Video
        fields = '__all__'

    def get_is_subscribed(self, obj):
        now = datetime.now()
        request = self.context.get('request')
        subscriptions = request.user.user_subscriptions
        if subscriptions.exists():
            subscribe = subscriptions.filter(grade=obj.grade, expiry_date__gte=now).first()
        # subscribe = Subscribe.objects.filter(user=request.user, grade=obj.grade, expiry_date__gte=now).first()
            if subscribe.exists():
                return subscribe.is_valid(now)
        return False

class InteractionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionType
        fields = "__all__"

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = "__all__"

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = "__all__"


# class ViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = View
#         fields = "__all__"