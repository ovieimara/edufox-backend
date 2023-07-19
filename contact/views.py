from django.shortcuts import render
from rest_framework import generics, status, mixins
from rest_framework.response import Response
from .serializers import ContactFormSerializer, ContactSerializer
from .models import Contact, ContactForm
from rest_framework.permissions import AllowAny


# Create your views here.


class ListCreateAPIContact(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = 'pk'
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ListCreateAPIContactForm(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = ContactForm.objects.all().order_by('pk')
    serializer_class = ContactFormSerializer
    lookup_field = 'pk'
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
