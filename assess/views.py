from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Test, Assessment, Level
from .serializers import TestSerializer, AssessmentSerializer, LevelSerializer
# from .permissions import IsStaffEditorPermission
# Create your views here.

class ListCreateUpdateAPITest(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Test.objects.select_related('subject', 'grade').all().order_by('subject', 'topic')
    serializer_class = TestSerializer
    # permission_classes = [IsAdminUser, IsStaffEditorPermission]
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


# class UpdateAPITest(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Test.objects.select_related('subject', 'grade').all()
#     serializer_class = TestSerializer
#     permission_classes = [IsAdminUser, IsStaffEditorPermission]

class ListCreateUpdateAPIAssessment(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Assessment.objects.select_related('user').all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

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

# class UpdateAPIAssessment(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Assessment.objects.select_related('user').all()
#     serializer_class = AssessmentSerializer

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

    