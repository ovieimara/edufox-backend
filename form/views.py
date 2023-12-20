from django.shortcuts import render
from rest_framework import generics, status, mixins

from form.models import Waiter
from form.serializers import WaiterSerializer
from rest_framework.response import Response

from notify.views import send_email_with_template


# Create your views here.
class ListCreateUpdateAPIWaiter(mixins.CreateModelMixin, mixins.ListModelMixin,  mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Waiter.objects.all().order_by('pk')
    serializer_class = WaiterSerializer
    lookup_field = 'pk'
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk') is not None:
            return self.retrieve(request, *args, **kwargs)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # if not kwargs.get('pk') and request.user.is_staff:
        email = request.data.get('email')
        # response = self.create(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if instance and not instance.get('update', False):
            self.sendEmail(email)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def sendEmail(self, email):
        print('sending...', email)
        if email:
            substitutions = {
                "name": "John Doe",
                "subject": "Welcome to Edufox.",
                "message": "Thanks for signing up with Edufox",
                "from_email": "admin@edufoxng.com",
                "to_email": email
            }
            template_id = 'd-91c6653939d8457fb880715f801cb1d5'
            result = send_email_with_template(
                substitutions, template_id)
            if result and result.status_code == 202:
                print("Email sent successfully!")
            else:
                print(f"Error sending email: {result}")

    def put(self, request, *args, **kwargs):
        if kwargs.get('pk') and request.user.is_staff:
            return self.update(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        # Handle DELETE request logic
        if kwargs.get('pk') and request.user.is_staff:
            return self.destroy(request, *args, **kwargs)
        return Response(status.HTTP_403_FORBIDDEN)
