from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from .models import (Grade, Subject, Lecturer, Video, Rate, Comment, 
InteractionType, Interaction, Resolution)
# from assess.models import  Test, Assessment
from .serializers import (GradeSerializer, SubjectSerializer, LecturerSerializer, 
VideoSerializer, RateSerializer, CommentSerializer, InteractionTypeSerializer, 
InteractionSerializer, ResolutionSerializer)
from .permissions import IsStaffEditorPermission
from django.core.paginator import Paginator, EmptyPage


# Create your views here.
class ListCreateAPIGrades(generics.ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        if self.request.user.is_staff:
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
    queryset = Video.objects.select_related('grade', 'subject').all().order_by('pk')
    serializer_class = VideoSerializer
    filterset_fields = ['grade', 'subject', 'topic', 'lesson']
    ordering_fields = ['title', 'topic']
    search_fields = ['title', 'descriptions', 'topic', 'lesson', 'tags', 'subject__name', 'subject__description', 'grade__name', 'grade__description']
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # print('USER: ', self.request.user, self.request.user.is_staff)
        if self.request.user.is_staff:
            return super().perform_create(serializer)
        return status.HTTP_403_FORBIDDEN


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


class ListCreateAPIResolution(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Resolution.objects.all()
    serializer_class = ResolutionSerializer
    lookup_field = 'pk'
    # permission_classes = [IsStaffEditorPermission]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return None
