from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .models import (Grade, Subject, Lecturer, Video, Rate, Comment, 
InteractionType, Interaction, Test, Assessment)
from .serializers import (GradeSerializer, SubjectSerializer, LecturerSerializer, 
VideoSerializer, RateSerializer, CommentSerializer, InteractionTypeSerializer, 
InteractionSerializer, TestSerializer, AssessmentSerializer)
from .permissions import IsStaffEditorPermission

# Create your views here.
class ListCreateAPIGrades(generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        if self.request.user.IsStaffEditorPermission:
            return super().perform_create(serializer)
        return status.HTTP_403_FORBIDDEN

class UpdateAPIGrades(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateAPISubject(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class UpdateAPISubject(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateAPILecturer(generics.ListCreateAPIView):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    # permission_classes = [IsAdminUser, IsStaffEditorPermission]


class UpdateAPILecturer(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]


class ListCreateAPIVideo(generics.ListCreateAPIView):
    queryset = Video.objects.select_related('grade', 'subject').all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class UpdateAPIVideo(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.select_related('grade', 'subject').all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateAPIRate(generics.ListCreateAPIView):
    queryset = Rate.objects.select_related('video').all()
    serializer_class = RateSerializer

class UpdateAPIRate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rate.objects.select_related('video').all()
    serializer_class = RateSerializer

class ListCreateAPIComment(generics.ListCreateAPIView):
    queryset = Comment.objects.select_related('video').all()
    serializer_class = CommentSerializer

class UpdateAPIComment(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('video').all()
    serializer_class = CommentSerializer

class ListCreateAPIInteractionType(generics.ListCreateAPIView):
    queryset = InteractionType.objects.all()
    serializer_class = InteractionTypeSerializer

class UpdateAPIInteractionType(generics.RetrieveUpdateDestroyAPIView):
    queryset = InteractionType.objects.all()
    serializer_class = InteractionTypeSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateAPIInteraction(generics.ListCreateAPIView):
    queryset = Interaction.objects.select_related('user', 'video', 'type').all()
    serializer_class = InteractionSerializer

class UpdateAPIInteraction(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interaction.objects.select_related('user', 'video', 'type').all()
    serializer_class = InteractionSerializer

class ListCreateAPITest(generics.ListCreateAPIView):
    queryset = Test.objects.select_related('subject', 'grade').all()
    serializer_class = TestSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class UpdateAPITest(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interaction.objects.select_related('subject', 'grade').all()
    serializer_class = TestSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateAPIAssessment(generics.ListCreateAPIView):
    queryset = Interaction.objects.select_related('user').all()
    serializer_class = AssessmentSerializer

class UpdateAPIAssessment(generics.RetrieveUpdateDestroyAPIView):
    queryset = Interaction.objects.select_related('user').all()
    serializer_class = AssessmentSerializer