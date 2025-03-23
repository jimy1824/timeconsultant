from rest_framework import serializers
from constructor import models


class PageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PagesDetailsContent
        fields = ['id', 'title', 'category', 'description']


class PagesDetailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PagesDetailsContent
        fields = ['id', 'title', 'category']
