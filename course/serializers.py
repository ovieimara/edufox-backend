from datetime import datetime, timedelta
from os import read
from traceback import print_tb
from rest_framework import serializers
from course.abc import TitleEditor
from edufox import sanitize

from edufox.sanitize import BleachSanitizer, Cleanup, Sanitizer
from .models import (Grade, Comment, Rate, Subject, Lecturer,
                     Video, Interaction, Event, Resolution, Topic, Lesson)
# from assess.models import  Test, Assessment
from subscribe.models import GradePack, Subscribe
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.db.models import Q
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


class RateSerializer(serializers.ModelSerializer, Cleanup):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Rate
        fields = ['user', 'rating', 'video', 'created']

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        return super().validate(attrs)

    def create(self, validated_data):

        request = self.context.get('request')
        user = request.user if request else ''
        video = request.data.get('video')
        rate = request.data.get('rating')

        if not rate:
            rate = -1
            validated_data['rating'] = rate

        rate_queryset = Rate.objects.filter(video__pk=video, user=user)

        if rate_queryset.exists():
            return super().update(rate_queryset.first(), validated_data)

        if user and user.is_authenticated:
            validated_data['user'] = request.user
            return super().create(validated_data)
        return validated_data


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


class VideoSerializer(serializers.ModelSerializer, Cleanup):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    topics = serializers.ChoiceField(choices=[], write_only=True)
    lessons = serializers.ChoiceField(choices=[], write_only=True)
    title = serializers.CharField(max_length=255, allow_blank=True)
    video_id = serializers.CharField(max_length=255, allow_blank=True, validators=[
                                     UniqueValidator(queryset=Video.objects.all())])

    # lesson = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Video
        fields = '__all__'
        # exclude = ['grade', 'subject', 'topic', 'lesson']
        extra_kwargs = {'topics': {'write_only': True},
                        'topic': {'read_only': True},
                        'lesson': {'read_only': True},
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
        topics_queryset = Topic.objects.all().order_by(
            'chapter').values('title', 'chapter')
        lessons_queryset = Lesson.objects.all().order_by('num').values('title', 'num')

        # fill the lesson titles from the video titles
        # queryset = Lesson.objects.all()
        # for lesson in queryset:
        #     # print('lesson: ', lesson.title)
        #     video = lesson.lesson_videos.all().filter(subject__pk=2)
        #     if video.exists():
        #         if not lesson.title and lesson.subject.pk == 2:
        #             print('lesson: ', lesson.pk, ' ', video.first().title)
        #             # print(dir(lesson))
        #             lesson.title = video.first().title
        #             lesson.save()

        subject = None
        if view:
            subject = view.kwargs.get('subject')
            # print(view.kwargs)
        if subject:
            topics = topics_queryset.filter(
                subject__pk=subject).values('title', 'chapter')
            lessons = lessons_queryset.filter(
                subject__pk=subject).values('title', 'num')

            # print(topics)
            # subject_obj = Subject.objects.get(pk=subject)
            my_choices = [(topic.get(
                'title'), f"{topic.get('chapter')}. {topic.get('title')}") for topic in topics if topic]
            lesson_choices = [(lesson.get(
                'title'), f"{lesson.get('num')}. {lesson.get('title')}") for lesson in lessons if lesson]

            self.fields['subject'].initial = subject

        if not subject:
            my_choices = [(topic.get(
                'title'), f"{topic.get('chapter')}. {topic.get('title')}") for topic in topics_queryset if topic]
            lesson_choices = [(lesson.get(
                'title'), f"{lesson.get('num')}. {lesson.get('title')}") for lesson in lessons_queryset if lesson]

        self.fields['topics'].choices = my_choices
        self.fields['lessons'].choices = lesson_choices

    # def get_lesson(self, obj):
    #     return obj.lesson.num

    def get_is_subscribed(self, obj):
        subscribed = ''
        request = self.context.get('request')
        user = request.user
        # print('request: ', request)
        if user and user.is_authenticated:
            # subscriptions = request.user.subscriptions_user.all().order_by(
            #     "-created")
            grades = obj.grade.all()
            lesson_grades = [grade.pk for grade in grades]
            subscriptions = user.subscriptions_user.filter(
                Q(payment_method__expires_date__gt=timezone.now())
            ).order_by("-created")

            # subscription = subscriptions[0]
            # for sub in subscriptions:
            # print('subscriptions:', subscriptions)
            # grade_pack = subscription.grade
            # subscription_grades = grade_pack.grades

            # extras_grades = [grade.pk - 1, grade.pk + 1, grade.pk + 2]

            # grades_set = set(grades)
            # for pk in subscription_grades:
            #     try:
            #         g = Grade.objects.get(pk=pk)

            #         if g.name in grades:
            #             print("G: ", g.name, grades[0])
            #             subscribed = subscription
            #         subscription_grades.append(g)

            #     except Grade.DoesNotExist as ex:
            #         print('grade object error: ', ex)

            #     print("subscription: ", subscribed)
            # for grade in subscription_grades:
            #     if grade in grades_set:
            #         print('NAME: ', grade.name)
            #         subscribed = subscription

            # if subscriptions.exists():
            #     print(subscriptions[0])
            # for g in obj.grade:
            # subscription = subscriptions.first()
            # grade = subscription.grade

            # subscribed = subscriptions.filter(
            #     grade__in=obj.grade.all()).first()
            # print('subscriptions: ', list(subscriptions))

            # subscription_obj = subscriptions.filter(
            #     Q(grade__grades__overlap=lesson_grades)
            # )
            # print("subscriptions: ", subscriptions.first().grade.grades,
            #       type(subscriptions.first().grade.grades))
            # subscription_obj = subscriptions.filter(
            #     Q(grade__grades__contains=lesson_grades) &
            #     Q(
            #         payment_method__expires_date__gt=timezone.now())
            # )
            # Prefetch subscriptions and store them in a dictionary
            subscriptions_dict = {
                sub.user_id: sub for sub in subscriptions.prefetch_related(
                    Prefetch(
                        'grade',
                        queryset=GradePack.objects.filter(
                            grades__overlap=lesson_grades),
                        to_attr='matching_grades'
                    )
                )
            }

            subscription_obj = subscriptions_dict.get(user.id)
            # print("subscription_obj", subscriptions_dict)

            if subscription_obj:

                return True

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
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        editor = TitleEditor()
        topic = attrs.get('topics')
        lessons = attrs.get('lessons')
        video_title = attrs.get('title')
        video_id = attrs.get('video_id')
        tags = attrs.get('tags')
        subject = attrs.get('subject')
        description = attrs.get('description')
        start_end_credits = attrs.get('start_end_credits')

        if subject:
            subject = Subject.objects.filter(pk=subject.pk)
            if subject.exists():
                subject = subject.first()

        if topic:
            topic = Topic.objects.filter(title=topic)
            if topic.exists():
                topic = topic.first()

        if lessons:
            videoId = words = ''
            lesson = Lesson.objects.filter(title=lessons)
            if lesson.exists():
                lesson = lesson.first()
                # words = lesson.title
                words, videoId = editor.get_video_title_id(lesson.title)

                if not video_title:
                    attrs['title'] = words
                    # attrs['title'] = words[:len(
                    #     words) - length]
                    # print('title2: ', attrs.get('title'))

                if not description:
                    attrs['description'] = words
                    # attrs['description'] = words[:len(
                    #     words) - length]

                if not video_id:

                    attrs['video_id'] = videoId

                if videoId:
                    lesson.title = words
                    lesson.save()

                if not tags:
                    attrs['tags'] = editor.get_video_tag(
                        subject.name, topic.title)

        attrs['topic'] = topic
        attrs['lesson'] = lesson
        if not start_end_credits:
            attrs['start_end_credits'] = '00:07'

        return super().validate(attrs)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

    def validate_name(self, value):
        if Event.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('This field must be unique.')
        return value


class VideoSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = "__all__"


class InteractionSerializer(serializers.ModelSerializer, Cleanup):
    # type = serializers.ChoiceField(
    #     choices=['END', 'EXIT', 'PAUSE', 'PLAY', 'START', 'STOP'])
    user = serializers.StringRelatedField(read_only=True)
    # video = serializers.StringRelatedField(read_only=True)
    video = VideoSerializer(read_only=True)

    class Meta:
        model = Interaction
        fields = "__all__"
        # depth = 1

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        request = self.context.get('request')
        # print('USER: ', request)
        user = request.user
        if user and user.is_authenticated:
            attrs['user'] = request.user

        return super().validate(attrs)

# class SeekSerializer(serializers.ModelSerializer):
#     direction = serializers.ChoiceField(choices=['FW', 'RW'])
#     class Meta:
#         model = Seek
#         fields = "__all__"

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     print('USER: ', user)

    #     user = request.user
    #     # event = validated_data.get('event')
    #     # print('USER: ', user)
    #     # event_obj = Event.objects.get(name__iexact=event)
    #     # validated_data['event'] = event_obj.pk

    #     if user and user.is_authenticated:
    #         validated_data['user'] = request.user
    #         return super().create(validated_data)
    #     return validated_data

# class AssessmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Assessment
#         fields = "__all__"


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer, Cleanup):
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

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())

        title = attrs['title']
        grade = attrs['grade']
        grades = [gr.pk for gr in grade]

        queryset = Topic.objects.filter(
            Q(title=title) & Q(grade__pk__in=grades))

        if queryset.exists():
            raise serializers.ValidationError(
                'title & grades fields must be unique.')

        attrs['title'] = title.title()
        return super().validate(attrs)

    # def validate_title(self, value):
    #     if Topic.objects.filter(title=value).exists():
    #         raise serializers.ValidationError('This field must be unique.')
    #     return value

    def get_grade(self, obj):
        # return GradeSerializer(obj.grade.all(), many=True).data
        return [grade.name for grade in obj.grade.all()]


# class ChapterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Chapter
#         fields = "__all__"

class LessonSerializer(serializers.ModelSerializer, Cleanup):
    # subject = serializers.StringRelatedField()
    topics = serializers.ChoiceField(
        choices=[], write_only=True, allow_blank=True)
    topic = serializers.StringRelatedField()
    # grades = serializers.SerializerMethodField()
    # title = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ['pk', 'num', 'title', 'topic',
                  'subject', 'grade', 'topics']
        # exclude = ('created', 'updated')
        extra_kwargs = {'topics': {'write_only': True},
                        'topic': {'read_only': True}
                        }

    # def create(self, validated_data):
    #     return super().create(validated_data)

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        # editor = TitleEditor()

        title = attrs.get('title')
        grade = attrs.get('grade')
        topic = attrs.get('topics')

        # video_id = words = ''
        # if title:
        #     # title = title.replace("_", " ")
        #     title_arr = title.split('_')
        #     last_word = title_arr.pop() if title_arr else ''
        #     # words = ' '.join(title_arr)
        #     # last_word.split('-')

        #     # title = title.strip('_converted.mp4')
        #     # words = title
        #     arr = last_word.split('-')
        #     if len(arr) > 1:
        #         _, video_id = arr

        #     title = f"{' '.join(title_arr).strip().title()}{'-' if video_id else ''}{video_id}"
        topic_obj = Topic.objects.filter(title=topic)
        if topic_obj.exists():
            attrs['topic'] = topic_obj.first()
        # attrs['title'] = editor.get_lesson_title(title).strip()

        grades = [gr.pk for gr in grade]
        # print('GRADE: ', grades)
        queryset = Lesson.objects.filter(
            Q(title=title) & Q(grade__pk__in=grades))

        if queryset.exists():
            raise serializers.ValidationError(
                'title & grade fields must be unique.')

        return super().validate(attrs)

    # def validate_title(self, value):
    #     if Lesson.objects.filter(title=value).exists():
    #         raise serializers.ValidationError('This field must be unique.')
    #     return value

    def __init__(self, *args, my_choices=None, **kwargs):
        if not my_choices:
            my_choices = []
        super().__init__(*args, **kwargs)
        # print('kwargs: ', kwargs.get('context').get("request").GET)
        view = self.context.get('view')
        topics_queryset = Topic.objects.all().order_by(
            'chapter').values('title', 'chapter')
        subject = None
        if view:
            subject = view.kwargs.get('subject')
            # print(view.kwargs)
        if subject:
            grades = []
            topics = topics_queryset.filter(
                subject__pk=subject).values('title', 'chapter')
            subject_obj = Subject.objects.get(pk=subject)
            if subject_obj:
                grades = subject_obj.grade.all()

            my_choices = [(topic.get(
                'title'), f"{topic.get('chapter')}. {topic.get('title')}")for topic in topics]
            self.fields['subject'].initial = subject
            self.fields['topic'].initial = 1
            self.fields['grade'].initial = grades[0].name if len(
                grades) > 0 else ''

        if not subject:
            my_choices = [(topic.get(
                'title'), f"{topic.get('chapter')}. {topic.get('title')}")for topic in topics_queryset]

        self.fields['topics'].choices = my_choices
        # self.fields['grade'].initial = [grade.name for grade in grades.grade.all()]

    def get_grades(self, obj):
        # print('GRADES: ', obj.grade.all())
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

    # def validate(self, attrs):
    #     title = attrs.get('topics')
    #     topic = Topic.objects.filter(title=title).first()
    #     attrs['topic'] = topic

    #     return super().validate(attrs)


class TopicSubjectSerializer(serializers.ModelSerializer, Cleanup):
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

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        return super().validate(attrs)
