from rest_framework import serializers
from constructor import models


class CountryListViewSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'type']

    def get_type(self, obj):
        return 'Country'


class CityListViewSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    country_id = serializers.SerializerMethodField()
    state_id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = models.City
        fields = ['id', 'name', 'type', 'country', 'country_id', 'state_id']

    def get_country(self, obj):
        return obj.state.country.name

    def get_country_id(self, obj):
        return obj.state.country.id

    def get_state_id(self, obj):
        return obj.state.id

    def get_type(self, obj):
        return 'City'


class StateDetailListViewSerializer(serializers.ModelSerializer):
    cities = CityListViewSerializer(source='city_set', many=True)
    type = serializers.SerializerMethodField()
    country_id = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'type', 'cities', 'country_id']

    def get_type(self, obj):
        return 'State'

    def get_country_id(self, obj):
        return obj.country.id


class CountryDetailListViewSerializer(serializers.ModelSerializer):
    states = StateDetailListViewSerializer(source='state_set', many=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'type', 'states']

    def get_type(self, obj):
        return 'Country'


class RegionListViewSerializer(serializers.ModelSerializer):
    countries = CountryListViewSerializer(source='country_set', many=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = models.Region
        fields = ['id', 'name', 'type', 'countries']

    def get_type(self, obj):
        return 'Region'
