from rest_framework import serializers
from constructor import models


# from .institute import InstituteRankingDetailSerializer


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name', 'logo', 'icon', 'description']


class StateWithCountrySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'country']


class CityDetailWithStateCountrySerializer(serializers.ModelSerializer):
    state = StateWithCountrySerializer()

    class Meta:
        model = models.City
        fields = ['id', 'name', 'state']


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name', 'logo', 'icon', 'order', 'popular']


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ['id', 'name', 'state']


class CityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ['id', 'name', 'state']


class StateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = ['id', 'name', 'country']


class StateWithCitiesListSerializer(serializers.ModelSerializer):
    cities = CityListSerializer(source="city_set", many=True, read_only=True)

    class Meta:
        model = models.State
        fields = ['id', 'name', 'cities']


class StateDetailSerializer(serializers.ModelSerializer):
    cities = CityListSerializer(source="city_set", many=True, read_only=True)
    country = CountryListSerializer(read_only=True)

    class Meta:
        model = models.State
        fields = ['id', 'name', 'region', 'country', 'cities']


class CountryDetailSerializer(serializers.ModelSerializer):
    states = StateListSerializer(source="state_set", many=True, read_only=True)

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'short_description', 'description', 'states', 'logo', 'icon']


class CountryWithAllCitiesSerializer(serializers.ModelSerializer):
    state = StateListSerializer(read_only=True)

    class Meta:
        model = models.City
        fields = ['id', 'name', 'description', 'state']


class InstituteRankingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstituteRanking
        fields = ['id', 'ranking_type', 'value']


class InstituteCampusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'city']


class InstituteListSerializer(serializers.ModelSerializer):
    # state = StateListSerializer(read_only=True)
    institute_ranking = InstituteRankingDetailSerializer(source='instituteranking_set', many=True)
    campuses = InstituteCampusListSerializer(source='institutecampus_set', many=True)

    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'logo', 'institute_type', 'sector', 'campuses', 'institute_ranking','institute_panel']


class CountryWithAllCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name', 'discipline', 'degree_level', 'specialization']


class CountryWithAllScholarshipSerializer(serializers.ModelSerializer):
    number_of_scholarships = serializers.SerializerMethodField()

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'number_of_scholarships']

    def get_number_of_scholarships(self, obj):
        return obj.number_of_scholarships


# counties with states and cities
class StateWithAllCitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ['id', 'name']


class CountryStatesWithAllCitiesSerializer(serializers.ModelSerializer):
    cities = StateWithAllCitiesSerializer(source="city_set", many=True, read_only=True)

    class Meta:
        model = models.State
        fields = ['id', 'name', 'cities']


class AllCountriesWithAllStatesAndCitiesSerializer(serializers.ModelSerializer):
    states = CountryStatesWithAllCitiesSerializer(source="state_set", many=True, read_only=True)

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'states']


class CountryFAQASerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CountryFAQA
        fields = ['id', 'question', 'answer']


class CountryMapSerializer(serializers.ModelSerializer):
    institute_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'latitude', 'longitude', 'institute_count', 'logo', 'icon']

    def get_institute_count(self, obj):
        return models.InstituteCampus.objects.filter(city__state__country=obj).count()


class CountryStatesMapSerializer(serializers.ModelSerializer):
    campus_count = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'latitude', 'longitude', 'campus_count']

    def get_campus_count(self, obj):
        return obj.campus_count


class CountryStatesCityMapSerializer(serializers.ModelSerializer):
    campus_count = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'latitude', 'longitude', 'campus_count']

    def get_campus_count(self, obj):
        return obj.campus_count


class CityCampusesMapSerializer(serializers.ModelSerializer):
    institute = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'campus', 'latitude', 'longitude', 'institute']

    def get_institute(self, obj):
        return {'id': obj.institute.id, 'name': obj.institute.institute_name}
