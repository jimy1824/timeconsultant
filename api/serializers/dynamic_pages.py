from rest_framework import serializers
from constructor import models


class DynamicPagesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DynamicPages
        fields = ['id', 'name', 'heading', 'content']


class DynamicPagesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DynamicPages
        fields = ['id', 'name', 'heading']
