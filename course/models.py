from django.db import models
from django.contrib.auth.models import User

class Grade(models.Model):
    code = models.CharField(max_length=100, null=False, default='', unique=True)
    name = models.CharField(max_length=255, null=False, default='', unique=True)
    description = models.TextField(null=True, default=True)
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)

    def __str__(self) -> str:
        return self.name

# Create your models here.

class View(models.Model):
    user = models.ForeignKey(User, related_name='user_view', on_delete=models.CASCADE)
    start_time = models.TextField(null=True, blank=True, default='')
    stop_time = models.CharField(max_length=127, null=True, default='')
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    # interaction_type = models.CharField(max_length=127, null=True, default='')

class Subject(models.Model):
    code = models.CharField(db_index=True, max_length=127)
    name = models.CharField(db_index=True, null=False, unique=True, max_length=255)
    description = models.TextField(null=True, blank=True, default='')
    credits = models.SmallIntegerField(default=0)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField( null=True, auto_now=True)

    def __str__(self) -> str:
        return self.name

class Lecturer(models.Model):
    first_name = models.CharField(db_index=True, null=False, max_length=255)
    last_name = models.CharField(db_index=True, null=False, max_length=255)
    subject = models.ManyToManyField(Subject, related_name='lecturer_subjects')

    def __str__(self) -> str:
        return self.first_name

class Video(models.Model):
    title = models.CharField(db_index=True, max_length=255, default='')
    description = models.TextField(null=True, blank=True, default='')
    duration = models.CharField(db_index = True, max_length=255, null=True, blank=True, default='')
    resolution = models.CharField(db_index = True, max_length=255, null=True, blank=True, default='')
    thumbnail =  models.URLField(null=True)
    topic = models.CharField(db_index = True, max_length=255, null=True, blank=True, default='')
    lesson = models.SmallIntegerField(db_index = True, null=True, blank=True, default=0)
    url =  models.URLField(null=True, blank=True, default='')
    tags =  models.JSONField(null=True, blank=True, default=dict)
    subject = models.ForeignKey(Subject, related_name='subjects', on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, related_name='grades', null=True, on_delete=models.SET_NULL)
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    # views = models.ForeignKey(View, related_name='views', on_delete=models.CASCADE)
    # likes = models.SmallIntegerField(null=True, blank=True, default=0)
    # rating = models.IntegerField(null=True, blank=True, default=0)
    # comments = models.IntegerField(null=True, blank=True, default=0)


    def __str__(self) -> str:
        return self.title

class Rate(models.Model):
    user = models.ForeignKey(User, related_name='user_rating', on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    video = models.ForeignKey(Video, related_name='ratings', null=True, on_delete=models.SET_NULL)

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='user_comments', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True, default='')
    created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)
    video = models.ForeignKey(Video, related_name='video_comments', null=True, on_delete=models.SET_NULL)


class InteractionType(models.Model):
    code = models.CharField(max_length=127, null=True, default='')
    name = models.CharField(db_index=True, max_length=127, default='')
    description = models.TextField(blank=True, default='')

    def __str__(self) -> str:
        return self.name

class Interaction(models.Model):
    user = models.ForeignKey(User, related_name='interactions', on_delete=models.CASCADE)
    type = models.ForeignKey(InteractionType, related_name='types', null=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(Video, related_name='videos', null=True, on_delete=models.SET_NULL)
    video_time_of_interaction = models.CharField(db_index=True, null=True, max_length=50, default='')
    seek_fwd = models.CharField(db_index=True, null=True, max_length=50, default='')
    seek_prev = models.CharField(db_index=True, null=True, max_length=50, default='')
    created = models.DateField(db_index=True, null=True, auto_now_add=True)
    updated = models.DateTimeField(db_index=True, null=True, auto_now=True)


class Test(models.Model):
    code = models.CharField(max_length=255, null=True, default='')
    subject = models.ForeignKey(Subject, related_name='test_subjects', null=True, on_delete=models.SET_NULL)
    question = models.JSONField(default=dict)
    options = models.JSONField(null=True, default=dict)
    grade = models.ForeignKey(Grade, related_name='test_grade', null=True, on_delete=models.SET_NULL)
    difficulty_level = models.CharField(null=True, max_length=127, default='')

    def __str__(self) -> str:
        return self.question

class Assessment(models.Model):
    user = models.ForeignKey(User, related_name='assessments', on_delete=models.CASCADE)
    test = models.ManyToManyField(Test, related_name='tests')
    answer = models.JSONField(default=dict)
    result = models.SmallIntegerField(default=0)
