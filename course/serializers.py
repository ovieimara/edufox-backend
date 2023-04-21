from datetime import datetime, timedelta
from rest_framework import serializers
from .models import (Grade, Comment, Rate, Subject, Lecturer, Video, Interaction, Resolution, Topic, Lesson)
# from assess.models import  Test, Assessment
from subscribe.models import Subscribe
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


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
    topics = serializers.ChoiceField(choices=[], write_only=True)
    lessons = serializers.ChoiceField(choices=[], write_only=True)

    # lesson = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Video
        fields = '__all__'
        # exclude = ['grade', 'subject', 'topic', 'lesson']
        extra_kwargs = {'topics': {'write_only': True},
                'topic': {'read_only' : True},
                'lesson': {'read_only' : True},
                }
        # validators = [
        #     serializers.UniqueTogetherValidator(
        #         queryset=Video.objects.all(),
        #         fields=('lesson', 'topic'),
        #         message='Combination of lesson and topic already exists.'
        #     )
        # ]
        # depth = 1

    
    def __init__(self, *args, my_choices=None, lesson_choices=None, **kwargs):
        if not my_choices:
            my_choices = []
        if not lesson_choices:
            my_choices = []

        super().__init__(*args, **kwargs)
        # print('kwargs: ', kwargs.get('context').get("request").GET)
        view = self.context.get('view')
        topics_queryset = Topic.objects.all().order_by('chapter').values('title', 'chapter')
        lessons_queryset = Lesson.objects.all().order_by('num').values('title', 'num')

        subject = None
        if view:
            subject = view.kwargs.get('subject')
            # print(view.kwargs)
        if subject:
            topics = topics_queryset.filter(subject__pk=subject).values('title', 'chapter')
            lessons = lessons_queryset.filter(subject__pk=subject).values('title', 'num')

            # print(topics)
            # subject_obj = Subject.objects.get(pk=subject)
            my_choices = [(topic.get('title'), f"{topic.get('chapter')}. {topic.get('title')}") for topic in topics]
            lesson_choices = [(lesson.get('title'), f"{lesson.get('num')}. {lesson.get('title')}") for lesson in lessons]

            self.fields['subject'].initial = subject

        if not subject:
            my_choices = [(topic.get('title'), f"{topic.get('chapter')}. {topic.get('title')}") for topic in topics_queryset]
            lesson_choices = [(lesson.get('title'), f"{lesson.get('chapter')}. {lesson.get('title')}") for lesson in lessons_queryset]
            

        
        self.fields['topics'].choices = my_choices
        self.fields['lessons'].choices = lesson_choices

    # def get_lesson(self, obj):
    #     return obj.lesson.num

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            subscriptions = request.user.subscriptions_user.all()
            if subscriptions.exists():
                # for g in obj.grade:
                subscribed = subscriptions.filter(grade__in=obj.grade.all()).first()
                if subscribed:
                    return subscribed.is_valid(datetime.now())
                return False
            return False
        return False
    
    def get_topics(self, obj):
        view = self.context.get('view')
        subject = None
        if view:
            subject = view.kwargs.get('subject')
            print(view.kwargs)
        if subject:
            topics = Topic.objects.filter(subject__pk=subject).values('title')
            print(topics)
            return [topic.get('title') for topic in topics]
        
        return []
    
    def validate(self, attrs):
        title = attrs.get('topics')
        value = attrs.get('lessons')

        topic = Topic.objects.filter(title=title)
        if topic:
            topic = topic.first()
        lesson = Lesson.objects.filter(title=value)
        if lesson:
            lesson = lesson.first()

        attrs['topic'] = topic
        attrs['lesson'] = lesson

        return super().validate(attrs)

# class InteractionTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InteractionType
#         fields = "__all__"

class InteractionSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=['END', 'EXIT', 'PAUSE','PLAY', 'START', 'STOP'])
    class Meta:
        model = Interaction
        fields = "__all__"

# class SeekSerializer(serializers.ModelSerializer):
#     direction = serializers.ChoiceField(choices=['FW', 'RW'])
#     class Meta:
#         model = Seek
#         fields = "__all__"

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

class TopicSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    class Meta:
        model = Topic
        exclude = ('created', 'updated')
        # extra_kwargs = {
        #         'title': {
        #             'validators': [
        #                 UniqueValidator(
        #                     queryset=Topic.objects.all()
        #                 )
        #             ]
        #         }
        #     }
    def validate_title(self, value):
        if Topic.objects.filter(title=value).exists():
            raise serializers.ValidationError('This field must be unique.')
        return value
    
    def get_grade(self, obj):
        # return GradeSerializer(obj.grade.all(), many=True).data
        return [grade.name for grade in obj.grade.all()]
    


# class ChapterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Chapter
#         fields = "__all__"

class LessonSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    topics = serializers.ChoiceField(choices=[], write_only=True)
    topic = serializers.StringRelatedField()
    grades = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=255)
    
    class Meta:
        model = Lesson
        fields = ['num', 'title', 'topic', 'subject', 'grade', 'grades', 'topics']
        # exclude = ('created', 'updated')
        extra_kwargs = {'topics': {'write_only': True},
                        'topic': {'read_only' : True}
                        }
    def validate_title(self, value):
        if Topic.objects.filter(title=value).exists():
            raise serializers.ValidationError('This field must be unique.')
        return value

    def __init__(self, *args, my_choices=None, **kwargs):
        if not my_choices:
            my_choices = []
        super().__init__(*args, **kwargs)
        # print('kwargs: ', kwargs.get('context').get("request").GET)
        view = self.context.get('view')
        topics_queryset = Topic.objects.all().order_by('chapter').values('title', 'chapter')
        subject = None
        if view:
            subject = view.kwargs.get('subject')
            # print(view.kwargs)
        if subject:
            grades = []
            topics = topics_queryset.filter(subject__pk=subject).values('title', 'chapter')
            subject_obj = Subject.objects.get(pk=subject)
            if subject_obj:
                grades = subject_obj.grade.all()
            
            my_choices = [(topic.get('title'), f"{topic.get('chapter')}. {topic.get('title')}")for topic in topics]
            self.fields['subject'].initial = subject
            self.fields['topic'].initial = 1
            self.fields['grade'].initial = grades[0].name if len(grades) > 0 else ''

        if not subject:
            my_choices = [(topic.get('title'), f"{topic.get('chapter')}. {topic.get('title')}")for topic in topics_queryset]
        
        self.fields['topics'].choices = my_choices
        # self.fields['grade'].initial = [grade.name for grade in grades.grade.all()]
    
    def get_grades(self, obj):
        return [grade.name for grade in obj.grade.all()]
    
    
    def get_topics(self, obj):
        view = self.context.get('view')
        subject = None
        if view:
            subject = view.kwargs.get('subject')
            # print(view.kwargs)
        if subject:
            topics = Topic.objects.filter(subject__pk=subject).values('title')
            print(topics)
            return [topic.get('title') for topic in topics]
        
        return []
    
    # def create(self, validated_data):
    #     print('validated_data: ', validated_data)
    #     return super().create(validated_data)
    
    
    def validate(self, attrs):
        title = attrs.get('topics')
        topic = Topic.objects.filter(title=title).first()
        attrs['topic'] = topic

        return super().validate(attrs)
    
class TopicSubjectSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField()
    class Meta:
        model = Topic
        fields = "__all__"
    
    def get_topic(self, obj):
        request = self.context.get('request')
        subject = request.kwargs.get('subject')
        if subject:
            topics = Topic.objects.filter(subject__pk=subject).values('title')
            return topics
        
        return obj.topic


        