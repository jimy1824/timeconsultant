from rest_framework import serializers
from constructor import models


class DisciplineListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ['id', 'name', 'key']


class DisciplineWithCourseCountSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Discipline
        fields = ['id', 'name', 'courses_count']

    def get_courses_count(self, obj):
        return obj.course_count


class DisciplineDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ['id', 'logo', 'icon', 'name', 'short_description', 'description']


class SpecializationDetailViewSerializer(serializers.ModelSerializer):
    discipline_id = serializers.SerializerMethodField()
    discipline_name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = models.Specialization
        fields = ['id', 'name', 'discipline_id', 'discipline_name', 'type']

    def get_discipline_id(self, obj):
        print(self.context.get("discipline_id"),'self.context.get("discipline_id")')
        return self.context.get("discipline_id")

    def get_discipline_name(self, obj):
        return self.context.get("discipline_name")

    def get_type(self, obj):
        return 'Specialization'


class SpecializationRelatedCourseCountSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Specialization
        fields = ['id', 'name', 'course_count']

    def get_course_count(self, obj):
        return obj.course_count


class CourseTitleDetailViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseTitle
        fields = ['id', 'display_name']
