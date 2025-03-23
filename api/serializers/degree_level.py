from rest_framework import serializers
from constructor import models


class DegreeLevelViewSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.DegreeLevel
        fields = ['id', 'name', 'key', 'level_type']

    def get_name(self, obj):
        return obj.display_name


class CourseTitlelViewSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.CourseTitle
        fields = ['id', 'name', 'key']

    def get_name(self, obj):
        return obj.display_name
