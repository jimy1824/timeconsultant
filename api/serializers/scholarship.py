from rest_framework import serializers
from constructor import models
from .country import CountryListSerializer
from .institute import InstituteWithAllCampusSerializer
from .discipline import DisciplineListViewSerializer
from .degree_level import DegreeLevelViewSerializer


class ScholarshipTypeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.ScholarshipType
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.display_name


class ScholarshipTypeCountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    scholarship_count = serializers.SerializerMethodField()

    class Meta:
        model = models.ScholarshipType
        fields = ['id', 'name', 'key', 'scholarship_count']

    def get_name(self, obj):
        return obj.display_name

    def get_scholarship_count(self, obj):
        return obj.scholarship_count


class ScholarshipStartDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScholarshipStartDate
        fields = ['id', 'month', 'day', 'year']


class ScholarshipCloseDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScholarshipCloseDate
        fields = ['id', 'month', 'day', 'year']


class ScholarshipDetailSerializer(serializers.ModelSerializer):
    type = ScholarshipTypeSerializer(source='scholarship_type', many=True)
    discipline = DisciplineListViewSerializer(many=True)
    degree_level = DegreeLevelViewSerializer(many=True)
    institute = InstituteWithAllCampusSerializer()
    scholarship_start_date = ScholarshipStartDateSerializer(source='scholarshipstartdate_set', many=True)
    scholarship_close_date = ScholarshipCloseDateSerializer(source='scholarshipclosedate_set', many=True)

    class Meta:
        model = models.Scholarship
        fields = ['id', 'scholarship_name', 'type', 'scholarship_content', 'scholarship_value',
                  'nationality', 'scholarship_eligibility', 'how_to_apply', 'scholarship_link', 'discipline',
                  'degree_level', 'scholarship_courses', 'institute', 'scholarship_start_date',
                  'scholarship_close_date']


class ScholarshipListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scholarship
        fields = ['id', 'scholarship_name', 'scholarship_type', 'institute']


class CountryScholarshipListSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    type = ScholarshipTypeSerializer(source='scholarship_type', many=True)
    discipline = DisciplineListViewSerializer(many=True)
    degree_level = DegreeLevelViewSerializer(many=True)

    class Meta:
        model = models.Scholarship
        fields = ['id', 'country', 'scholarship_name', 'discipline', 'degree_level', 'type', 'institute',
                  'scholarship_value']

    def get_country(self, obj):
        try:
            country = models.Country.objects.filter(state__city__institutecampus__institute=obj.institute).first()
            return CountryListSerializer(country).data
        except AttributeError:
            return None
