from django.shortcuts import render

from rest_framework import generics, status, mixins
from rest_framework.response import Response
from .serializers import BannerSerializer
from .models import Banner

# Create your views here.


class ListCreateAPIBanner(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Banner.objects.all().order_by('num')
    serializer_class = BannerSerializer
    lookup_field = 'pk'
    # permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not kwargs.get('pk') and request.user.is_staff:
            return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return None
