from rest_framework import serializers
from constructor import models
from constructor.models import InstituteCampus
from .country import CityDetailWithStateCountrySerializer, CountryListSerializer, CountrySerializer


class CampusListWithLocationSerializer(serializers.ModelSerializer):
    city = CityDetailWithStateCountrySerializer()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city', 'address']


class InstituteWithAllCampusSerializer(serializers.ModelSerializer):
    campuses = CampusListWithLocationSerializer(source='institutecampus_set', many=True)

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'institute_type', 'sector', 'established', 'campuses']


class AllInstitutesSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'country']

    def get_country(self, obj):
        try:
            campus = obj.institutecampus_set.first()
            country = models.Country.objects.filter(state__city__institutecampus=campus).first()
            return CountryListSerializer(country).data
        except AttributeError:
            return None


class InstituteRankingDetailSerializer(serializers.ModelSerializer):
    ranking_value = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteRanking
        fields = ['id', 'ranking_type', 'ranking_value', 'value']

    def get_ranking_value(self, obj):
        try:
            value = obj.value
            value = value.replace('_', '0')
            value = value.replace('-', '0')
            value = value.replace('TBC', '0')
            value = value.replace('+', '')
            return int(value)
        except AttributeError:
            return 0
        except ValueError:
            return 0


class CampusNameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus']


class AllInstituteRankingsSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    campus = CampusNameListSerializer(source='institutecampus_set', many=True)
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)

    class Meta:
        model = models.Institute
        order = 'institute_ranking__ranking_value'
        fields = ['id', 'institute_name', 'country', 'campus', 'institute_ranking']

    def get_country(self, obj):
        try:
            campus = obj.institutecampus_set.first()
            country = models.Country.objects.filter(state__city__institutecampus=campus).first()
            return CountryListSerializer(country).data
        except AttributeError:
            return None


class InstituteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'institute_type', 'sector']


class InstituteDetailSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    campus_locations = serializers.SerializerMethodField()

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'institute_type', 'sector', 'established', 'logo',
                  'institute_short_description', 'institute_description',
                  'country', 'campus_locations']

    def get_country(self, obj):
        try:
            campus = InstituteCampus.objects.filter(institute=obj).first()
            if (campus):
                return CountrySerializer(campus.city.state.country).data
            return ''
        except AttributeError:
            return ''

    def get_campus_locations(self, obj):
        return CampusLocationsSerializer(obj.institutecampus_set.all(), many=True).data


class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name']


class StateDetailSerializer(serializers.ModelSerializer):
    country = CountryDetailSerializer()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'country']


class CityDetailSerializer(serializers.ModelSerializer):
    state = StateDetailSerializer()

    class Meta:
        model = models.City
        fields = ['id', 'name', 'state']


class InstituteRankingSerializer(serializers.ModelSerializer):
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'institute_type', 'institute_ranking', 'logo']


class InstituteNameSerializer(serializers.ModelSerializer):
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)
    institute_type = serializers.SerializerMethodField()
    sector = serializers.SerializerMethodField()

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'established', 'institute_type', 'sector', 'institute_ranking', 'logo',
                  'institute_panel']

    def get_institute_type(self, obj):
        return obj.get_institute_type_display()

    def get_sector(self, obj):
        return obj.get_sector_display()


class InstituteLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'logo', 'institute_description']


class CampusListSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer()
    institute = InstituteNameSerializer()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city', 'address', 'institute']


class CourseListWithCampusSerializer(serializers.ModelSerializer):
    campus = CampusListSerializer()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'discipline', 'campus']


class CampusDetailSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer()
    institute = InstituteNameSerializer()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city', 'address', 'institute']


class CampusDetailSearchSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer()
    institute = InstituteNameSerializer()
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city', 'institute', 'course_count']

    def get_course_count(self, obj):
        try:
            return obj.id__count
        except AttributeError:
            return len(obj.course_set.all())


class CampusLocationSerializer(serializers.ModelSerializer):
    institute = InstituteLocationSerializer()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'institute', 'latitude', 'longitude']


class CampusLocationsSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'latitude', 'longitude', 'city']

    def get_city(self, obj):
        return obj.city.name
