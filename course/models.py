from django.db import models
from django.contrib.auth.models import User


class Grade(models.Model):
    code = models.CharField(max_length=100, null=False,
                            default='', unique=True)
    name = models.CharField(max_length=255, null=False,
                            default='', unique=True)
    description = models.TextField(null=True, default=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class View(models.Model):
    user = models.ForeignKey(
        User, related_name='user_view', on_delete=models.CASCADE)
    start_time = models.TextField(null=True, blank=True, default='')
    stop_time = models.CharField(max_length=127, null=True, default='')
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    # interaction_type = models.CharField(max_length=127, null=True, default='')


class Subject(models.Model):
    code = models.CharField(db_index=True, max_length=127)
    name = models.CharField(db_index=True, null=False,
                            unique=True, max_length=255)
    grade = models.ManyToManyField(Grade, related_name="grade_subjects")
    description = models.TextField(null=True, blank=True, default='')
    credits = models.SmallIntegerField(default=0)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self) -> str:
        return self.name


class Lecturer(models.Model):
    first_name = models.CharField(db_index=True, null=False, max_length=255)
    last_name = models.CharField(db_index=True, null=False, max_length=255)
    subject = models.ManyToManyField(Subject, related_name='lecturer_subjects')

    def __str__(self) -> str:
        return self.first_name


class Resolution(models.Model):
    name = models.CharField(null=True, max_length=100, default='')
    size = models.CharField(null=True, max_length=100, default='')
    aspect_ratio = models.CharField(null=True, max_length=100, default='')
    media = models.CharField(null=True, max_length=100, default='')
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self) -> str:
        return self.name


class Topic(models.Model):
    chapter = models.SmallIntegerField(null=True, blank=True, default=0)
    subject = models.ForeignKey(
        Subject, related_name='subject_topics', null=True, on_delete=models.SET_NULL)

    title = models.CharField(
        db_index=True, max_length=255, null=True, default='')
    grade = models.ManyToManyField(Grade, related_name='grade_topics')
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return self.title
        # return f"{self.chapter}. {self.title}"

# class Chapter(models.Model):
#     num = models.SmallIntegerField(null=True, blank=True, default=0)
#     topic = models.ForeignKey(Topic, related_name='topic_chapters', null=True, on_delete=models.SET_NULL)
#     subject = models.ForeignKey(Subject, related_name='subject_chapters', null=True, on_delete=models.SET_NULL)
#     grade = models.ForeignKey(Grade, related_name='grade_chapters', null=True, default=1, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

#     def __str__(self) -> str:
#         return f"{self.num}. {self.topic}"
# class SubTopic(models.Model):
#     title = models.CharField(max_length=255, null=True, default='')
#     subject = models.ForeignKey(Subject, related_name='subject_subtopics', null=True, default=None, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)


class Lesson(models.Model):
    LEVEL_CHOICES = ()
    num = models.SmallIntegerField(null=True, blank=True, default=0)
    # title = models.CharField(db_index=True, max_length=255, default='')
    title = models.TextField(null=True, blank=True, default='')
    topic = models.ForeignKey(
        Topic, related_name='topic_lessons', on_delete=models.CASCADE)
    topics = models.CharField(
        max_length=255, choices=LEVEL_CHOICES, null=True, blank=True, default=[])
    subject = models.ForeignKey(
        Subject, related_name='subject_lessons', null=True, on_delete=models.SET_NULL)
    grade = models.ManyToManyField(Grade, related_name='grade_lessons')
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    # @property
    # def topics(self):
    #     return []
    # view = self.context.get('view')
    # subject = None
    # if view:
    #     subject = view.kwargs.get('subject')
    #     print(view.kwargs)
    # if subject:
    #     topics = Topic.objects.filter(subject__pk=subject).values('title')
    #     print(topics)
    #     return [topic.get('title') for topic in topics]

    def __str__(self) -> str:
        return f"{self.num}. {self.title}"


class Video(models.Model):
    video_id = models.CharField(
        max_length=255, default='000')
    lesson = models.ForeignKey(
        Lesson, related_name='lesson_videos', null=True, on_delete=models.SET_NULL)
    lessons = models.CharField(
        max_length=255, choices=(), null=True, default=[])
    title = models.CharField(db_index=True, max_length=255)
    description = models.TextField(null=True, blank=True, default='')
    duration = models.CharField(
        db_index=True, max_length=50, null=True, blank=True, default='')
    resolution = models.ForeignKey(
        Resolution, related_name='resolutions', null=True, on_delete=models.SET_NULL)
    thumbnail = models.URLField(null=True)
    # topic = models.CharField(db_index = True, max_length=255, null=True, blank=True, default='')
    topic = models.ForeignKey(
        Topic, related_name='topics', null=True, on_delete=models.SET_NULL)
    topics = models.CharField(
        max_length=255, choices=(), null=True, default=[])

    url = models.URLField(null=True, blank=True, default='')
    tags = models.TextField(null=True, blank=True, default=dict)
    subject = models.ForeignKey(
        Subject, related_name='subject_videos', null=True, on_delete=models.SET_NULL)
    grade = models.ManyToManyField(
        Grade, default=[], related_name='grade_videos')
    end_start_credits = models.CharField(
        max_length=50, null=True, blank=True, default='')
    start_end_credits = models.CharField(
        max_length=50, null=True, blank=True, default='')
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return self.title


class Rate(models.Model):
    user = models.ForeignKey(
        User, related_name='user_ratings', null=True, blank=True, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=-1)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    video = models.ForeignKey(
        Video, related_name='ratings', null=True, on_delete=models.SET_NULL)


class Comment(models.Model):
    user = models.ForeignKey(
        User, related_name='user_comments', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True, default='')
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    video = models.ForeignKey(
        Video, related_name='video_comments', null=True, on_delete=models.SET_NULL)

# class Seek(models.Model):
#     user = models.ForeignKey(User, related_name='seeks', null=True, default=1, on_delete=models.CASCADE)
#     direction = models.CharField(null=True, max_length=10, default='')
#     to_duration = models.CharField(null=True, max_length=50, default='')
#     from_duration = models.CharField(null=True, max_length=50, default='')
#     video = models.ForeignKey(Video, related_name='video_seeks', null=True, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)


# class Play(models.Model):
#     duration = models.CharField(null=True, max_length=10, default='')
#     video = models.ForeignKey(Video, related_name='video_comments', null=True, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)


# class Pause(models.Model):
#     duration = models.CharField(null=True, max_length=10, default='')
#     video = models.ForeignKey(Video, related_name='video_comments', null=True, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

# class Stop(models.Model):
#     duration = models.CharField(null=True, max_length=10, default='')
#     video = models.ForeignKey(Video, related_name='video_comments', null=True, on_delete=models.SET_NULL)
#     created = models.DateField(db_index=True, null=True, auto_now_add=True)
#     updated = models.DateTimeField(db_index=True, null=True, auto_now=True)


class Event(models.Model):
    name = models.CharField(db_index=True, max_length=127, default='')
    description = models.TextField(blank=True, default='')

    def __str__(self) -> str:
        return self.name


class Interaction(models.Model):
    user = models.ForeignKey(
        User, related_name='interactions', on_delete=models.CASCADE)
    # type = models.CharField(db_index=True, null=True,
    #                         max_length=50, default='')
    event = models.ForeignKey(
        Event, related_name='event', null=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(
        Video, related_name='videos', null=True, on_delete=models.SET_NULL)
    begin_duration = models.CharField(null=True, max_length=100, default='')
    end_duration = models.CharField(null=True, max_length=100, default='')
    # begin_duration = models.DecimalField(
    #     max_digits=10, decimal_places=4, default=0.0000)
    # end_duration = models.DecimalField(
    #     max_digits=10, decimal_places=4, null=True, blank=True, default=0.0000)
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    # seek_fwd = models.CharField(null=True, max_length=50, default='')
    # seek_prev = models.CharField(null=True, max_length=50, default='')
    # type = models.ForeignKey(InteractionType, related_name='types', null=True, on_delete=models.SET_NULL)

# class Test(models.Model):
#     code = models.CharField(max_length=255, null=True, default='')
#     subject = models.ForeignKey(Subject, related_name='test_subjects', null=True, on_delete=models.SET_NULL)
#     question = models.JSONField(default=dict)
#     options = models.JSONField(null=True, default=dict)
#     grade = models.ForeignKey(Grade, related_name='test_grade', null=True, on_delete=models.SET_NULL)
#     difficulty_level = models.CharField(null=True, max_length=127, default='')

#     def __str__(self) -> str:
#         return self.question

# class Assessment(models.Model):
#     user = models.ForeignKey(User, related_name='assessments', on_delete=models.CASCADE)
#     test = models.ManyToManyField(Test, related_name='tests')
#     answer = models.JSONField(default=dict)
#     result = models.SmallIntegerField(default=0)
