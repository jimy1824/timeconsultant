from rest_framework import serializers

from api.serializers.institute import CampusListWithLocationSerializer, CityDetailSerializer
from constructor import models
from api.serializers import discipline as disciplines_serializer, degree_level as degree_level_serializer, \
    course as course_serializer


class PathwayGroupListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.PathwayGroup
        fields = ['id', 'name', 'logo']

    def get_name(self, obj):
        return obj.display_name


class PathwayGroupDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.PathwayGroup
        fields = ['id', 'name', 'short_description', 'description', 'logo']

    def get_name(self, obj):
        return obj.display_name


class InstituteGroupSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteGroup
        fields = ['id', 'name', 'logo']

    def get_name(self, obj):
        return obj.display_name


class InstituteGroupListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteGroup
        fields = ['id', 'name', 'logo', 'short_description']

    def get_name(self, obj):
        return obj.display_name


class InstituteGroupDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteGroup
        fields = ['id', 'name', 'logo', 'short_description', 'content']

    def get_name(self, obj):
        return obj.display_name


class InstituteGroupWithUniversitiesSerializer(serializers.ModelSerializer):
    campuses = CampusListWithLocationSerializer(source='institutecampus_set', many=True)

    class Meta:
        model = models.Institute
        fields = ['id', 'logo', 'institute_name', 'institute_short_description', 'institute_description',
                  'institute_type', 'sector', 'established',
                  'campuses']


class InstituteRankingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstituteRanking
        fields = ['id', 'ranking_type', 'value']


class InstituteCampusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city']


class InstituteGroupWithUniversitiesListSerializer(serializers.ModelSerializer):
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)
    campuses = InstituteCampusListSerializer(source='institutecampus_set', many=True)
    institute_group = InstituteGroupSerializer()

    class Meta:
        model = models.Institute
        fields = ['id', 'logo', 'institute_name', 'sector', 'institute_group', 'campuses', 'institute_ranking']


class ApplyPortalSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.ApplyPortal
        fields = ['id', 'name', 'logo', 'short_description', 'description']

    def get_name(self, obj):
        return obj.display_name


class InstituteNameSerializer(serializers.ModelSerializer):
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)
    institute_group = InstituteGroupSerializer()

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'institute_group', 'established', 'institute_type', 'sector',
                  'institute_ranking', 'logo',
                  'institute_panel']


class CampusDetailSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer()
    institute = InstituteNameSerializer()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city', 'address', 'institute']


class InstituteGroupCourseDetailsSerializer(serializers.ModelSerializer):
    campus = CampusDetailSerializer()
    discipline = disciplines_serializer.DisciplineDetailViewSerializer()
    specialization = disciplines_serializer.SpecializationDetailViewSerializer()
    course_title = disciplines_serializer.CourseTitleDetailViewSerializer()
    degree_level = degree_level_serializer.DegreeLevelViewSerializer()
    course_duration = course_serializer.CourseDurationSerializer(source='courseduration_set', many=True)
    admission_schedule = course_serializer.CourseIntakeAndDeadLineSerializer(source='courseintakeanddeadline_set',
                                                                             many=True)
    fee = course_serializer.FeeDetailSerializer(source='coursefee_set', many=True)
    exams = course_serializer.CourseExamDetailSerializer(source='courseexam_set', many=True)
    source_links = course_serializer.CourseApplyDetailSerializer(source='courseapply_set', many=True)

    class Meta:
        model = models.Course
        fields = [field.name for field in models.Course._meta.fields] + ['course_duration', 'admission_schedule', 'fee',
                                                                         'exams', 'source_links']
