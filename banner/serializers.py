from rest_framework import serializers
from .models import Banner


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"

        extra_kwargs = {
            'name': {'read_only': True}}

    def validate(self, attrs):
        label = attrs.get('label')
        if label:
            words = label.split()
            name = '_'.join(words)
            attrs['name'] = name
        return super().validate(attrs)
