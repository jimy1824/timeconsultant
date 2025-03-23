from collections import defaultdict
import json
from django.http import HttpResponse
from django.db.models import Count, QuerySet
from rest_framework import viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from constructor import models
from api.serializers import region_serializer
from django.conf import settings
from django.core.cache import cache
CACHE_TTL = getattr(settings, 'CACHE_TTL')


class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all().order_by('name')
    serializer_classes = {
        'list': region_serializer.RegionListViewSerializer,
        'retrieve': region_serializer.RegionListViewSerializer,
        'popular_countries': region_serializer.CountryListViewSerializer,
        'all_countries': region_serializer.CountryDetailListViewSerializer,
        'popular_cities': region_serializer.CityListViewSerializer,
        # 'institutes': country.InstituteListSerializer
    }
    default_serializer_class = region_serializer.RegionListViewSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='all_regions', url_path='all')
    def all_regions(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        serializer = self.get_serializer(models.Region.objects.all().order_by('name'), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='popular_countries', url_path='popular-countries')
    def popular_countries(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        serializer = self.get_serializer(models.Country.objects.filter(popular=True).order_by('name'), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='all_countries', url_path='all-countries')
    def all_countries(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        if 'all_countries_with_states_cities' in cache:
            data = cache.get('all_countries_with_states_cities')
            return Response(data)
        else:
            serializer = self.get_serializer(models.Country.objects.all().order_by('name'), many=True)
            cache.set('all_countries_with_states_cities', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)

    @action(detail=False, methods=['get'], name='popular_cities', url_path='popular-cities')
    def popular_cities(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        serializer = self.get_serializer(models.City.objects.filter(popular=True).order_by('name'), many=True)
        return Response(serializer.data)
