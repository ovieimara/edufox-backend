from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Grade, Subject, Lecturer
from .serializers import GradeSerializer, SubjectSerializer, LecturerSerializer
from .permissions import IsStaffEditorPermission

# Create your views here.
class ListCreateAPIGrades(generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

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
    permission_classes = [IsAdminUser, IsStaffEditorPermission]

    def perform_create(self, serializer):
        subjects = serializer.validated_data.get('subject')
        subjects_list = []
        for i in range(len(subjects)):
            instance = Subject.objects.get(name=subjects[i])
            subjects_list.append(instance)
        if subjects_list:
            serializer.save(subject=subjects_list)

class UpdateAPILecturer(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminUser, IsStaffEditorPermission]