from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from course.models import Lesson, Subject, Grade, Topic


class Level(models.Model):
    code = models.CharField(max_length=127, null=True, default='')
    name = models.CharField(max_length=127, null=True, default='')

    def __str__(self) -> str:
        return self.name


class Answer(models.Model):
    answer = models.CharField


class Test(models.Model):
    CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
    )
    code = models.CharField(max_length=100, null=True, blank=True, default='')
    question = models.TextField(default='')
    # options = models.JSONField(default=dict)
    # option1 = models.TextField(default='')
    # option2 = models.TextField(default='')
    # option3 = models.TextField(default='')
    # option4 = models.TextField(default='')
    # option5 = models.TextField(default='')
    # option6 = models.TextField(default='')
    # valid_options = ArrayField(models.SmallIntegerField(), blank=True, default=list)
    # correct_answers = ArrayField(models.SmallIntegerField(), blank=True, default=list)
    # valid_options = models.CharField(max_length=2, choices=CHOICES, default=[])

    valid_answers = models.JSONField(null=True, default=list)
    options = models.JSONField(null=True, default=list)

    subject = models.ForeignKey(
        Subject, related_name='test_subjects', null=True, on_delete=models.SET_NULL)
    grade = models.ForeignKey(
        Grade, related_name='test_grade', null=True, on_delete=models.SET_NULL)
    # topic = models.CharField(max_length=100, null=True, blank=True, default='')
    topic = models.ForeignKey(
        Topic, related_name='topic_tests', null=True, on_delete=models.SET_NULL)
    lesson = models.ForeignKey(
        Lesson, related_name='lesson_tests', null=True, on_delete=models.SET_NULL)
    # lesson = models.SmallIntegerField(null=True, blank=True, default=0)
    level = models.ForeignKey(Level, related_name='difficulty_level',
                              null=True, blank=True, on_delete=models.SET_NULL, default=1)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self) -> str:
        return self.question

    # def __lt__(self, other):
    #     return self.topic.title < other.topic.title

    # def __gt__(self, other):
    #     return self.topic.title > other.topic.title


class Assessment(models.Model):
    CHOICES = (
        ('A', ''),
        ('B', ''),
        ('C', ''),
        ('D', ''),
        ('E', ''),
        ('F', ''),
    )
    user = models.ForeignKey(
        User, related_name='assessments', null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, related_name='tests',
                             default=1, on_delete=models.CASCADE)
    # answer = models.ManyToManyField(Test, related_name='answers', on_delete=models.CASCADE)
    # answer = models.CharField(max_length=1, choices=CHOICES, default=[])
    answer = models.JSONField(default=list)
    # status = models.SmallIntegerField(default=0)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)

    def __str__(self) -> str:
        return self.test.question
