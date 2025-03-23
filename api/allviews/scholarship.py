import json

from django.db.models import Count
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from constructor.choices import INTAKE_MONTHS
from constructor.paginator import ResultsSetPagination
from constructor import models
from api.serializers import scholarship
from api.query_helper import get_filtered_scholarships
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class ScholarshipTypeView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.ScholarshipType.objects.all()
    serializer_classes = {
        'list': scholarship.ScholarshipTypeSerializer,
        'retrieve': scholarship.ScholarshipTypeSerializer,
        # 'institutes': country.InstituteListSerializer,

    }
    default_serializer_class = scholarship.ScholarshipTypeSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class ScholarshipView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Scholarship.objects.all()
    serializer_classes = {
        'list': scholarship.ScholarshipListSerializer,
        'retrieve': scholarship.ScholarshipDetailSerializer,
        'all_scholarship': scholarship.ScholarshipDetailSerializer,
        'country_scholarship': scholarship.ScholarshipListSerializer,
        # 'scholarship_search': scholarship.CountryScholarshipListSerializer,
        'scholarship_search': scholarship.ScholarshipDetailSerializer,
        'institute_scholarship': scholarship.ScholarshipDetailSerializer,

    }
    default_serializer_class = scholarship.ScholarshipListSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='country_scholarship', url_path='country_scholarship')
    def country_scholarship(self, request, country_id, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        # test=models.InstituteCampus.objects.values('institute').distinct()
        # print(test[0])
        qs = get_filtered_scholarships(request)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='institute_scholarship', url_path='institute/(?P<institute_pk>[0-9]+)')
    def institute_scholarship(self, request, institute_pk, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        # test=models.InstituteCampus.objects.values('institute').distinct()
        # print(test[0])
        qs = models.Scholarship.objects.filter(institute__id=institute_pk).order_by('scholarship_name')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='scholarship_search', url_path='search')
    def scholarship_search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = get_filtered_scholarships(request)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='scholarship_related_disciplines',
            url_path='scholarship_related_disciplines')
    def scholarship_related_disciplines(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        scholarships = get_filtered_scholarships(request)
        disciplines = models.Discipline.objects.filter(scholarship__in=scholarships).annotate(
            scholarship_count=Count('scholarship'))
        results = []
        for discipline in disciplines:
            results.append(
                {'id': discipline.id, 'name': discipline.name, 'scholarship_count': discipline.scholarship_count})

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='scholarship_related_degree_levels',
            url_path='scholarship_related_degree_levels')
    def scholarship_related_degree_levels(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        scholarships = get_filtered_scholarships(request)
        scholarships = scholarships.distinct()
        degree_levels = models.DegreeLevel.objects.filter(scholarship__in=scholarships).annotate(
            scholarship_count=Count('scholarship'))

        results = [
            {'id': 1, 'name': 'Undergradute', 'type': 'undergradute', 'scholarship_count': 0, 'degree_levels': []},
            {'id': 2, 'name': 'Postgradute', 'type': 'postgradute', 'scholarship_count': 0, 'degree_levels': []},
            {'id': 3, 'name': 'Postgradute by Research', 'type': 'postgradute_by_research', 'scholarship_count': 0,
             'degree_levels': []},
        ]
        degree_levels_list = models.DegreeLevel.objects.all().order_by('order')
        for degree_level in degree_levels_list.filter(level_type='undergradute'):
            results[0]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'scholarship_count': 0,
                                                })

        for degree_level in degree_levels_list.filter(level_type='postgradute'):
            results[1]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'scholarship_count': 0,
                                                })
        for degree_level in degree_levels_list.filter(level_type='postgradute_by_research'):
            results[2]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'scholarship_count': 0,
                                                })

        for degree_level in degree_levels:
            if degree_level.level_type == 'undergradute':
                for index, obj in enumerate(results[0]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[0]['degree_levels'][index]['scholarship_count'] = degree_level.scholarship_count
                results[0]['scholarship_count'] = results[0]['scholarship_count'] + degree_level.scholarship_count
            if degree_level.level_type == 'postgradute':
                for index, obj in enumerate(results[1]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[1]['degree_levels'][index]['scholarship_count'] = degree_level.scholarship_count
                results[1]['scholarship_count'] = results[1]['scholarship_count'] + degree_level.scholarship_count
            if degree_level.level_type == 'postgradute_by_research':
                for index, obj in enumerate(results[2]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[2]['degree_levels'][index]['scholarship_count'] = degree_level.scholarship_count
                results[2]['scholarship_count'] = results[2]['scholarship_count'] + degree_level.scholarship_count

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

        # results = []
        # for degree_level in degree_levels:
        #     results.append(
        #         {'id': degree_level.id, 'name': degree_level.display_name,
        #          'scholarship_count': degree_level.scholarship_count})
        #
        # dump = json.dumps(results)
        # return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='scholarship_related_types',
            url_path='scholarship_related_types')
    def scholarship_related_types(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        scholarships = get_filtered_scholarships(request)
        scholarship_types = models.ScholarshipType.objects.filter(scholarship__in=scholarships).annotate(
            scholarship_count=Count('scholarship'))
        results = []
        for scholarship_type in scholarship_types:
            results.append(
                {'id': scholarship_type.id, 'name': scholarship_type.display_name,
                 'scholarship_count': scholarship_type.scholarship_count})

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='scholarship_related_years',
            url_path='scholarship_related_years')
    def scholarship_related_years(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        scholarships = get_filtered_scholarships(request)
        scholarship_deadlines = models.ScholarshipCloseDate.objects.filter(scholarship__in=scholarships,
                                                                           year__isnull=False).annotate(
            scholarship_count=Count('scholarship'))

        results = []
        for scholarship_deadlines in scholarship_deadlines:
            item, index = next(
                ((item, index) for index, item in enumerate(results) if item['year'] == scholarship_deadlines.year),
                (None, None))
            if item:
                item['scholarship_count'] = item['scholarship_count'] + scholarship_deadlines.scholarship_count
                results[index] = item

            else:
                results.append(
                    {'year': scholarship_deadlines.year,
                     'scholarship_count': scholarship_deadlines.scholarship_count})

        dump = json.dumps(results)

        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='scholarship_related_months',
            url_path='scholarship_related_months')
    def scholarship_related_months(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        scholarships = get_filtered_scholarships(request)
        scholarship_deadlines = models.ScholarshipCloseDate.objects.filter(scholarship__in=scholarships).annotate(
            scholarship_count=Count('scholarship'))

        results = []
        for key, value in INTAKE_MONTHS:
            results.append({'month': value, 'scholarship_count': 0})

        for deadline in scholarship_deadlines:
            for result in results:
                if deadline.month == result['month']:
                    result['scholarship_count'] = result['scholarship_count'] + deadline.scholarship_count
        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['get'], name='scholarship_related_countries',
            url_path='scholarship_related_countries')
    def scholarship_related_countries(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        if not bool(request.data) and 'scholarship_related_countries' in cache:
            return HttpResponse(cache.get('scholarship_related_countries'), content_type='application/json')
        # if not bool(request.data) and not 'scholarship_related_countries' in cache:
        #     print('staore data ')
        #     results = []
        #     countries = models.Country.objects.all()
        #     scholarships = models.Scholarship.objects.all()
        #     for country in countries:
        #         query = Q()
        #         query.add(Q(institute__institutecampus__city__state__country=country), Q.OR)
        #         query.add(Q(institute_name_organizational_scholarship__country=country), Q.OR)
        #         count = scholarships.filter(query).order_by('name').distinct('id').count()
        #         if count != 0:
        #             results.append({'id': country.id,
        #                             'name': country.name,
        #                             'scholarship_count': count,
        #                             'scholarship_logo': country.scholarship_logo,
        #                             })
        #     dump = json.dumps(results)
        #     cache.set('scholarship_related_countries', dump, timeout=CACHE_TTL)
        #     return HttpResponse(dump, content_type='application/json')
        #
        else:
            results = []
            countries = models.Country.objects.all()
            # scholarships = get_filtered_scholarships(request)
            scholarships = get_filtered_scholarships(request)
            for country in countries:
                # query = Q()
                # query.add(Q(institute__institutecampus__city__state__country=country), Q.OR)
                # query.add(Q(institute_name_organizational_scholarship__country=country), Q.OR)
                count = scholarships.filter(Q(institute__institutecampus__city__state__country=country) | Q(
                    institute_name_organizational_scholarship__country=country)).order_by('id').distinct('id').count()
                if count != 0:
                    results.append({'id': country.id,
                                    'name': country.name,
                                    'scholarship_count': count,
                                    'scholarship_logo': country.scholarship_logo,
                                    })
            results = json.dumps(results)
            cache.set('scholarship_related_countries', results, timeout=CACHE_TTL)
            return HttpResponse(results, content_type='application/json')

    @action(detail=False, methods=['post'], name='scholarship_related_institutes',
            url_path='scholarship_related_institutes')
    def scholarship_related_institutes(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        results = []
        # scholarships = get_filtered_scholarships(request)
        # institutes=scholarships.values_list('institute',flat=True)
        # institutes_list=
        institutes_list = models.Institute.objects.filter(
            institutecampus__city__state__country__in=request.data.get("countries")).values_list('id', flat=True)
        institutes = models.Institute.objects.filter(id__in=institutes_list).order_by('institute_name').annotate(scholarship_count=Count('scholarship'))

        for institute in institutes:
            results.append({'id': institute.id,
                            'name': institute.institute_name,
                            'scholarship_count': institute.scholarship_count,
                            })
        results = json.dumps(results)
        return HttpResponse(results, content_type='application/json')

    @action(detail=False, methods=['get'], name='all_scholarship',
            url_path='all')
    def all_scholarship(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        qs = models.Scholarship.objects.all()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ScholarshipCountryView(APIView):
    serializer_class = scholarship.ScholarshipListSerializer

    # permission_classes = (IsAuthenticated,)

    def get_object(self):
        return models.Scholarship.objects.all()

    # def post(self, request, *args, **kwargs):
    #     data = self.request.data.copy()
    #     data['user'] = self.request.user.id
    #     serializer = self.serializer_class(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({"message": CATEGORY_ADDED_SUCCESS}, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)
