from datetime import datetime, timedelta
from functools import lru_cache
import logging
from os import read
import os
import platform
import random
from re import sub
from traceback import print_tb
from typing import List
from urllib import request
import uuid
# from turtle import title
from venv import logger
from rest_framework import serializers
from client.library import AmazonDynamoDB, AmazonImageStore, GoogleCloudStorageRepo2, GoogleImageStore
from course.abc import TitleEditor
from edufox import sanitize
from edufox.constants import ANDROID, IOS, WEB

from edufox.sanitize import BleachSanitizer, Cleanup, Sanitizer
from .models import (Grade, Comment, Rate, SearchQuery, Subject, Lecturer, Thumbnail,
                     Video, Interaction, Event, Resolution, Topic, Lesson)
# from assess.models import  Test, Assessment
from subscribe.models import GradePack, Subscribe
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.db.models import Q
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from .icons import subjects


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
    # video_id = serializers.CharField(max_length=255, allow_blank=True, validators=[
    #     UniqueValidator(queryset=Video.objects.all())])

    # lesson = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Video
        # fields = '__all__'
        # fields = ['is_subscribed', 'topics', 'lessons', 'title', 'video_id']
        exclude = ['created', 'updated', 'resolution']
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

    # def validate_video_id(self, value):
    #     """
    #     Validate the 'video' field to ensure it's not empty.
    #     """
    #     if not value:
    #         raise serializers.ValidationError("Video field cannot be empty.")
    #     return value

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
        lesson_grades = []
        request = self.context.get('request')
        user = request.user if request is not None else ''
        # print('request: ', request)
        if user and user.is_authenticated:
            # subscriptions = request.user.subscriptions_user.all().order_by(
            #     "-created")
            if isinstance(obj, dict):
                grades = obj.get('grade')
                lesson_grades = grades
            else:
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

    def create(self, validated_data):

        request = self.context.get('request')
        user = request.user if request else ''
        title = validated_data.get('title')
        grades = validated_data.get('grade')
        subject = validated_data.get('subject')

        try:
            if user and user.is_authenticated:
                video_queryset = Video.objects.all().filter(
                    title__iexact=title, grade__in=grades, subject=subject)

                if video_queryset.exists():
                    video_instance = video_queryset.first()
                    duration = video_instance.duration
                    if duration:
                        validated_data['duration'] = duration
                    return super().update(video_instance, validated_data)

                return super().create(validated_data)
            return validated_data
        except Exception as ex:
            logging.error(
                f"createVideos: Validation error: {ex.message} {title}")

    def update(self, instance, validated_data):
        # instance = self.sanitize_attr(instance, BleachSanitizer())
        # validated_data = self.sanitize_attr(validated_data, BleachSanitizer())

        old_title = instance.title
        new_title = validated_data.get('title')
        video_id = instance.video_id
        subject = instance.subject
        lesson = instance.lesson
        old_description = instance.description
        new_description = validated_data.get('description')
        old_duration = instance.duration
        new_duration = validated_data.get('duration')
        old_subject = instance.subject
        new_subject = validated_data.get('subject')

        if old_title != new_title and new_title:
            lesson_obj = Lesson.objects.get(pk=lesson.pk)
            subject = Subject.objects.get(
                pk=subject.pk if type(subject) != str else subject)

            if subject and video_id:
                updated_data = {"partition_key_value": video_id,
                                "title": new_title, "subject_code": subject.code}
                amazonDynamoDB = AmazonDynamoDB()
                result = amazonDynamoDB.update_item_by_guid(updated_data)
                if result == f"{subject.code}/{new_title}":
                    lesson_obj.title = new_title
                    lesson_obj.save()
                    return super().update(instance, validated_data)

        if old_description != new_description and new_description:
            instance.description = new_description
            # instance.save()

        if old_duration != new_duration and new_duration:
            instance.duration = new_duration

        if old_subject != new_subject and new_subject:
            instance.subject = new_subject

        instance.save()

        return instance

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

    def validate(self, attrs):
        attrs = self.sanitize_attr(attrs, BleachSanitizer())
        lesson = ''
        # print("attrs: ", attrs)
        editor = TitleEditor()
        topic = attrs.get('topics')
        lessons = attrs.get('lessons')
        video_title = attrs.get('title')
        video_id = attrs.get('video_id')
        tags = attrs.get('tags')
        subject = attrs.get('subject')
        description = attrs.get('description')
        start_end_credits = attrs.get('start_end_credits')

        # if not video_id or not video_title:
        #     error_msg = f"{video_title} {video_id} field cannot be empty."

        #     raise serializers.ValidationError(error_msg)

        try:
            if subject:
                subject = Subject.objects.filter(
                    pk=subject.pk if type(subject) != str else subject)
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
                    # if description:
                    #     attrs['description'] = description
                    # print('description: ', description)

                    if description:
                        attrs['description'] = description

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

        except Exception as ex:
            logger.error(f'video validation: {ex}', video_title)

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
random_int_store: List = []


@lru_cache
def getRandomInt(size: int, lesson: int) -> int:
    # print("random_int_store: ", random_int_store)
    if size:
        num: int = 0
        if len(random_int_store) <= 0:
            num = random.randint(0, size - 1)
        else:
            num = random_int_store[-1]
            num += 1

        val = num % size
        random_int_store.append(val)

        return val

    return random.randint(0, 9)


class LessonSerializer(serializers.ModelSerializer, Cleanup):
    subject_name = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    topics = serializers.ChoiceField(
        choices=[], write_only=True, allow_blank=True)
    topic = serializers.StringRelatedField()
    thumbnail = serializers.SerializerMethodField(read_only=True)
    # grades = serializers.SerializerMethodField()
    # title = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ['pk', 'num', 'title', 'topic',
                  'subject', 'grade', 'topics', 'duration', 'thumbnail', 'subject_name']
        # exclude = ('created', 'updated')
        extra_kwargs = {'topics': {'write_only': True},
                        'topic': {'read_only': True}
                        }

    def get_subject_name(self, obj):
        subject = obj.subject
        if subject:
            try:
                subject_obj = Subject.objects.get(pk=subject.pk)
                return subject_obj.name
            except Subject.DoesNotExist:
                return ''

        return ''

    @lru_cache
    def getSignedUrls(self, subject: str) -> List:

        signed_urls = []

        repo = GoogleCloudStorageRepo2(
            f"img/subjects/{subject}/png", "edufox-bucket-2", 3600 * 3)
        image_objects = GoogleImageStore(repo)

        try:
            image_objects.list_images_in_bucket()
            signed_urls = image_objects.generate_signed_urls()

        except Exception as ex:
            logger.error('getSignedUrls error', ex)

        return signed_urls

    @lru_cache
    def getThumbnails(subject: int, platform: str) -> str:
        # print(subject, '.............')
        platforms = {IOS: 'svg', ANDROID: 'svg', WEB: 'svg'}
        # request = self.context.get('request')
        # platform = request.query_params.get('platform', 'svg')
        image_type = platforms.get(platform, 'svg') if platform else 'svg'
        urls = []

        # print("request: ", request.query_params.get('platform'))

        if subject:
            try:
                thumbnails_queryset = Thumbnail.objects.filter(
                    subject=subject, image_type=image_type)
                # thumbnails_queryset = subject.subject_thumbnails.filter(
                #     image_type=image_type)
                # print("thumbnail.url: ", list(thumbnails_queryset))
                if thumbnails_queryset.exists():
                    for thumbnail in thumbnails_queryset:
                        # print("thumbnail.url: ", thumbnail.url)
                        urls.append(thumbnail.url)
            except Exception as ex:
                logging.error(
                    f"getThumbnails: Subject error: {ex.message}")
        # print(urls)
        return urls

    def get_thumbnail(self, obj: Lesson) -> str:
        if obj:
            request = self.context.get('request')
            platform = request.query_params.get('platform', 'svg')
            # subject = obj.subject.code
            # print("obj: ", obj.get(
            #     'subject'))
            subject_instance = obj.get(
                'subject') if isinstance(obj, dict) else obj.subject

            lesson_pk = obj.get(
                'pk') if isinstance(obj, dict) else obj.pk
            # print("lesson_instance: ", lesson_instance)
        # subject_instance = Subject.objects.get(pk=subject.pk)

        # thumbnails = ['https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame229.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame230.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame231.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame241.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321460.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321461.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321462.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321463.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321464.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321465.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321466.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321467.png',
        #               'https://storage.googleapis.com/edufox-bucket-2/topics_thumbnails/Frame427321468.png']
        thumbnails = [
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num1.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num10.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num13.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num2.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num3.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num4.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num5.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num6.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num7.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num8.svg',
            'https://storage.googleapis.com/edufox-bucket-2/img/subjects/mathematics/svg/num9.svg'
        ]

        # if subject in subjects:
        #     thumbnails = subjects.get(subject)

        # random_integer = random.randint(0, len(thumbnails) - 1)
        # return thumbnails[random_integer] if random_integer > -1 else thumbnails[0]

        # image_objects = AmazonImageStore(os.environ.get(
        #     'AWS_THUMBNAIL_BUCKET'), os.environ.get('AWS_DISTRIBUTION_ID'))
        # print("subject_instance: ", subject_instance.pk)
        urls = LessonSerializer.getThumbnails(subject_instance.pk, platform)
        # print("url: ", url)
        if urls:
            # thumbnails = urls
            return urls[getRandomInt(len(urls), lesson_pk)]

        # print(lesson_pk)

        return thumbnails[random.randint(0, 9)]

    def get_duration(self, obj):
        # print('obj:', obj)
        if obj:
            try:
                video = obj.lesson_videos.all()
                # print("video: ", video.first().duration)
                return video.first().duration if video.exists() else ''
            except Exception as ex:
                logger.error('duration error', obj)
                return ''
        return ''

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
        # for grad in grade:
        #     print('GRADE:', type(grad))
        grades = [gr.pk for gr in grade if isinstance(grade,
                                                      Grade)]
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
            # print(topics)
            return [topic.get('title') for topic in topics]

        return []

    def create(self, validated_data):

        request = self.context.get('request')
        user = request.user if request else ''
        title = validated_data.get('title')
        grades = validated_data.get('grade')
        subject = validated_data.get('subject')

        if user and user.is_authenticated:
            lesson_queryset = Lesson.objects.all().filter(
                title__iexact=title, grade__in=grades, subject=subject)
            # print("lesson_queryset: ", lesson_queryset)
            if lesson_queryset.exists():
                return super().update(lesson_queryset.first(), validated_data)

            return super().create(validated_data)
        return validated_data

    def update(self, instance, validated_data):
        old_title = instance.title
        new_title = validated_data.get('title')
        # video_id = validated_data.get('video_id')
        subject = validated_data.get('subject')
        if old_title != new_title and subject:
            # if True:
            video = instance.lesson_videos.all()
            print(old_title, new_title, instance.pk, video)
            if video.exists():
                video = video.first()
            subject = Subject.objects.get(
                pk=subject.pk if type(subject) != str else subject)

            if subject and video:
                updated_data = {"partition_key_value": video.video_id,
                                "title": new_title, "subject_code": subject.code}
                amazonDynamoDB = AmazonDynamoDB()
                result = amazonDynamoDB.update_item_by_guid(updated_data)
                if result == f"{subject.code}/{new_title}":
                    video.title = new_title
                    video.save()
                    return super().update(instance, validated_data)

        return instance


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


class ThumbnailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Thumbnail
        fields = "__all__"

    def create(self, validated_data):

        request = self.context.get('request')
        user = request.user if request else ''
        subject = validated_data.get('subject')
        url = validated_data.get('url')

        if user and user.is_authenticated:
            thumbnail_queryset = Thumbnail.objects.filter(url=url)
            if thumbnail_queryset.exists():
                return super().update(thumbnail_queryset.first(), validated_data)

            return super().create(validated_data)
        return validated_data


class SearchQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = SearchQuery
        fields = ['pk', 'query']

# class RandomIntSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = RandomInt
#         fields = "__all__"

# class ListItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ListItem
#         fields = "__all__"


# class ListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = List
#         fields = "__all__"
