from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Test, Assessment, Level
from .serializers import TestSerializer, AssessmentSerializer, LevelSerializer
from course.models import Grade, Lesson, Subject, Topic
from django.shortcuts import get_object_or_404
from .permissions import IsStaffEditorPermission
# Create your views here.


class ListCreateAPITest(generics.ListCreateAPIView):
    '''
    Retrieve Test questions for the subject, the grade, under a topic and lesson
    example request url '/tests?grade=grade&subject=subject&topic=topic&lesson=lesson'
    '''
    queryset = Test.objects.select_related(
        'subject', 'grade').all().order_by('subject__name', 'topic')
    serializer_class = TestSerializer
    # filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    # ordering_fields = ['title', 'topic']
    # search_fields = ['title', 'topic', 'topic_name', 'lesson', 'lesson_name', 'lesson_pk', 'tags', 'subject__name', 'subject__description', 'grade__name', 'grade__pk', 'grade__description']

    def get_queryset(self):
        grade = self.request.query_params.get('grade')

        subject = self.request.query_params.get('subject')
        topic = self.request.query_params.get('topic')
        level = self.request.query_params.get('level')
        lesson = self.request.query_params.get('lesson')
        tests = Test.objects.select_related(
            'subject', 'grade', 'topic', 'lesson').order_by('subject', 'topic')
        if grade:
            # print("grade:", type(grade))
            grade_instance = ''
            if not grade.isnumeric():
                grade_instance = get_object_or_404(Grade, name=grade)
            if grade.isnumeric():
                # print("grade:", grade.replace(" ", ""))
                grade_instance = get_object_or_404(Grade, pk=grade)

            tests = tests.filter(grade=grade_instance)

        if subject:
            subject_instance = ''
            if not subject.isnumeric():
                subject_instance = get_object_or_404(Subject, name=subject)
            if subject.isnumeric():
                subject_instance = get_object_or_404(Subject, pk=subject)

            tests = tests.filter(subject=subject_instance)

        if topic:
            topic_instance = ''
            if not topic.isnumeric():
                topic_instance = get_object_or_404(Topic, name=topic)
            if topic.isnumeric():
                topic_instance = get_object_or_404(Topic, pk=topic)

            tests = tests.filter(topic=topic_instance)

        if lesson:
            lesson_instance = ''
            if not lesson.isnumeric():
                lesson_instance = get_object_or_404(Lesson, name=lesson)
            if lesson.isnumeric():
                lesson_instance = get_object_or_404(Lesson, pk=lesson)

            tests = tests.filter(lesson=lesson_instance)

        if level:
            level_instance = ''
            if not level.isnumeric():
                level_instance = get_object_or_404(Level, name=level)
            if level.isnumeric():
                level_instance = get_object_or_404(Level, pk=level)

            tests = tests.filter(level=level_instance)

        return tests

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            return super().perform_create(serializer)
        return Response(status=status.HTTP_403_FORBIDDEN)

    # permission_classes = [AllowAny]
    # permission_classes = [IsAdminUser, IsStaffEditorPermission]
    # def get(self, request, *args, **kwargs):
    #     if kwargs.get('pk') is not None:
    #         return self.retrieve(request, *args, **kwargs)

    #     return self.list(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     if not kwargs.get('pk') and request.user.is_staff:
    #         return self.create(request, *args, **kwargs)
    #     return Response(status=status.HTTP_403_FORBIDDEN)

    # def put(self, request, *args, **kwargs):
    #     if kwargs.get('pk') and request.user.is_staff:
    #         return self.update(request, *args, **kwargs)
    #     return Response(status=status.HTTP_403_FORBIDDEN)


class UpdateAPITest(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.select_related('subject', 'grade').all()
    serializer_class = TestSerializer
    permission_classes = [IsStaffEditorPermission]

# class ListCreateUpdateAPIAssessment(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
#     queryset = Assessment.objects.select_related('user').all()
#     serializer_class = AssessmentSerializer
#     permission_classes = [IsAuthenticated]
#     filterset_fields = ['user', 'test__grade', 'test__subject', 'topic', 'lesson']

#     def get(self, request, *args, **kwargs):
#         if kwargs.get('pk') is not None:
#             kwargs.get('grade')
#             return self.retrieve(request, *args, **kwargs)

#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         if not kwargs.get('pk') and request.user.is_staff:
#             return self.create(request, *args, **kwargs)
#         return Response(status=status.HTTP_403_FORBIDDEN)

#     def put(self, request, *args, **kwargs):
#         if kwargs.get('pk') and request.user.is_staff:
#             return self.update(request, *args, **kwargs)
#         return Response(status=status.HTTP_403_FORBIDDEN)


class UpdateAPIAssessment(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assessment.objects.select_related('user').all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]


class ListCreateAPIAssessment(generics.ListCreateAPIView):
    '''
    list the authenticated user's test questions(assessments) taken. You can provide query parameters to filter the assessments. The query parameters include: grade, subject, topic, lesson and level e.g
    /assess?subject=subject&grade=grade
    '''
    queryset = Assessment.objects.select_related('user').all().order_by('pk')
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        response = []
        grade = self.request.query_params.get('grade')
        subject = self.request.query_params.get('subject')
        topic = self.request.query_params.get('topic')
        level = self.request.query_params.get('level')
        lesson = self.request.query_params.get('lesson')
        assessments = self.request.user.assessments.all().order_by('pk')
        if grade:
            grade_instance = get_object_or_404(Grade, name=grade)
            # print(grade_instance)
            assessments = assessments.filter(test__grade=grade_instance)

        if subject:
            subject_instance = get_object_or_404(Subject, name=subject)
            # print(subject_instance)
            assessments = assessments.filter(test__subject=subject_instance)

        if topic:
            assessments = assessments.filter(test__topic=topic)

        if lesson:
            assessments = assessments.filter(test__lesson=lesson)

        if level:
            assessments = assessments.filter(test__level=level)

        return assessments

    def create(self, request, *args, **kwargs):
        user = request.user
        if user and not user.is_anonymous:
            data = request.data
            # updated_data = [ques.update([("user", user)]) for ques in data]
            serializer = self.get_serializer(
                data=data, many=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status.HTTP_201_CREATED)
            # return super().create(request, *args, **kwargs)
        return Response('not authenticated', status.HTTP_401_UNAUTHORIZED)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     if user and not user.is_anonymous:
    #         serializer.save(user=user)

    #     data = self.request.data

        # return Response(status.HTTP_401_UNAUTHORIZED)
        # return super().perform_create(serializer)


class ListCreateUpdateAPILevel(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    lookup_field = 'pk'
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
