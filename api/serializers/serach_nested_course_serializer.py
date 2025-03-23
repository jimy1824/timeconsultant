from constructor import models
from rest_framework import serializers


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name']


class DisciplineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ['id', 'name']


class DegreeLevelListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.DegreeLevel
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.display_name


class SpecializationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Specialization
        fields = ['id', 'name']


class CourseListSerializer(serializers.ModelSerializer):
    campus = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'campus']

    def get_campus(self, obj):
        return obj.campus.campus + ' ' + obj.campus.city.name + ' ' + obj.campus.city.state.name
