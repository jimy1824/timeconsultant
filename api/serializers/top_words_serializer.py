from rest_framework import serializers
from constructor import models


class DegreeLevelSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.DegreeLevel
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.display_name


class TopKeyWordSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    degree_level = DegreeLevelSerializer()

    class Meta:
        model = models.TopKeyWords
        fields = ['id', 'name', 'degree_level']

    def get_name(self, obj):
        return obj.word
