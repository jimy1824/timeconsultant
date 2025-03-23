from collections import defaultdict
import json
from django.http import HttpResponse
from django.db.models import Count, QuerySet
from rest_framework import viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.helper import get_ranking
from api.serializers.degree_level import DegreeLevelViewSerializer
from constructor import models
from api.serializers import country, institute, course, scholarship, discipline
from constructor.choices import INTAKE_MONTHS
from constructor.helper import headers
from constructor.paginator import ResultsSetPagination

from datetime import timedelta
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

datetime.today()


class CountryView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Country.objects.all()
    serializer_classes = {
        'countries': country.CountryListSerializer,
        'list': country.CountryListSerializer,
        'retrieve': country.CountryDetailSerializer,
        'states': country.CountryDetailSerializer,
        'cities': country.CountryWithAllCitiesSerializer,
        'institutes': country.InstituteListSerializer,
        'institutes_suggestion': country.InstituteListSerializer,
        # 'courses': country.CountryWithAllCoursesSerializer,
        'courses': course.CourseDetailsSerializer,
        'scholarships': country.CountryWithAllScholarshipSerializer,
        'country_scholarships': scholarship.CountryScholarshipListSerializer,
        'countries_states_cities': country.AllCountriesWithAllStatesAndCitiesSerializer,
        'country_institutes_ranking': institute.InstituteRankingSerializer,
        'country_discipline_related_specializations': discipline.SpecializationRelatedCourseCountSerializer,
        'country_discipline_related_institutes': country.InstituteListSerializer,
        'country_faqas': country.CountryFAQASerializer,
        'countries_map': country.CountryMapSerializer,
        'states_map': country.CountryStatesMapSerializer,
        'cities_map': country.CountryStatesCityMapSerializer,
        'cities_campuses_map': country.CityCampusesMapSerializer,
        'state_campuses_map': country.CityCampusesMapSerializer,
    }
    default_serializer_class = country.CountryDetailSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], url_path='all-countries')
    def countries(self, request, *args, **kwargs):
        """
        Returns  all countries list`.
        """
        if 'all-countries' in cache:
            return Response(cache.get('all-countries'))
        else:
            qs = models.Country.objects.all().order_by('name')
            serializer = self.get_serializer(qs, many=True)
            cache.set('all-countries', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)

    @action(detail=True, methods=['get'], name='states', url_path='states')
    def states(self, request, *args, **kwargs):
        """
        Returns  states list by country id with count`.
        """
        qs = self.get_object()
        serializer = self.get_serializer(qs)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='states', url_path='cities')
    def cities(self, request, *args, **kwargs):
        """
        Returns  cities list by country id with count`.
        """
        country_instance = self.get_object()
        qs = models.City.objects.filter(state__country=country_instance)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], name='institutes', url_path='institutes',
            serializer_class=institute.InstituteNameSerializer)
    def institutes(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        country_instance = self.get_object()
        ids = list(set(
            models.Institute.objects.filter(institutecampus__city__state__country=country_instance).values_list('id',
                                                                                                                flat=True)))
        qs = models.Institute.objects.filter(id__in=ids)
        if request.data.get("institute_type"):
            qs = qs.filter(institute_type__in=request.data.get("institute_type"))
        if request.data.get("order"):
            if request.data.get("order") == 1:
                qs = qs.order_by('institute_name')
            if request.data.get("order") == 2:
                qs = qs.order_by('-institute_name')
            if request.data.get("order") == 3:
                qs = qs.order_by('institute_panel')
            if request.data.get("order") == 4:
                # orderbyList = ['institute_panel', '-institute_name']
                # qs = qs.order_by(*orderbyList)
                qs = qs.order_by('-institute_panel')
        else:
            qs = qs.order_by('institute_name')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], name='institutes_suggestion', url_path='institutes_suggestion')
    def institutes_suggestion(self, request, *args, **kwargs):
        country_instance = self.get_object()
        # if country_instance.name in cache:
        #     qs = cache.get(country_instance.name)
        # else:
        #     qs = models.Institute.objects.filter(institutecampus__city__state__country=country_instance)
        #     cache.set(country_instance.name, qs, timeout=CACHE_TTL)
        ids = list(set(
            models.Institute.objects.filter(institutecampus__city__state__country=country_instance).values_list('id',
                                                                                                                flat=True)))
        qs = models.Institute.objects.filter(id__in=ids)
        if request.data.get("name"):
            qs = qs.filter(institute_name__icontains=request.data.get("name"))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='courses', url_path='courses')
    def courses(self, request, *args, **kwargs):
        """
        Returns list of courses by country`.
        """
        country_instance = self.get_object()
        qs = models.Course.objects.filter(campus__city__state__country=country_instance).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='countries_states_cities', url_path='countries_states_cities')
    def countries_states_cities(self, request, *args, **kwargs):
        """
        Returns list of  countries with all states and cities`.
        """
        qs = models.Country.objects.all().order_by('name')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country_scholarships', url_path='scholarships')
    def scholarships(self, request, *args, **kwargs):
        """
        Returns list of  countries with scholarship count`.
        """
        countries_list1 = models.Scholarship.objects.values_list('institute__institutecampus__city__state__country',
                                                                 flat=True).distinct()
        countries_list2 = models.Scholarship.objects.values_list('institute_name_organizational_scholarship__country',
                                                                 flat=True).distinct()
        countries_list = countries_list1 + countries_list2
        qs = models.Country.objects.filter(id__in=countries_list)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='scholarships')
    def country_scholarships(self, request, *args, **kwargs):
        """
        Returns list of scholarships  with respect to  country`.
        """
        country_instance = self.get_object()
        scholarship_list = models.Scholarship.objects.filter(
            institute__institutecampus__city__state__country=country_instance)

        qs = scholarship_list
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='disciplines')
    def country_disciplines(self, request, *args, **kwargs):
        """
        Returns list of disciplines  with respect to  country`.
        """
        country_instance = self.get_object()
        cache_id = str(country_instance.id) + country_instance.name
        dump = []
        if cache_id in cache:
            dump = cache.get(cache_id)
        else:
            qs = models.Institute.objects.filter(institutecampus__city__state__country=country_instance).order_by(
                'id').distinct('id')
            courses = models.Course.objects.filter(campus__institute__in=qs).order_by('name')
            qs = courses.values('discipline').distinct()
            disciplines = models.Discipline.objects.filter(id__in=qs)
            my_list = []
            for discipline in disciplines:
                qs = courses.filter(discipline=discipline)
                undergradute_degree_level_ids = qs.filter(degree_level__level_type='undergradute').values(
                    'degree_level').distinct()
                undergradute_degree_level = models.DegreeLevel.objects.filter(
                    id__in=undergradute_degree_level_ids).order_by('order')
                undergradute_serializer = DegreeLevelViewSerializer(undergradute_degree_level, many=True)

                postgradute_degree_level_ids = qs.filter(degree_level__level_type='postgradute').values(
                    'degree_level').distinct()
                postgradute_degree_level = models.DegreeLevel.objects.filter(
                    id__in=postgradute_degree_level_ids).order_by(
                    'order')
                postgradute_serializer = DegreeLevelViewSerializer(postgradute_degree_level, many=True)

                research_degree_level_ids = qs.filter(degree_level__level_type='postgradute_by_research').values(
                    'degree_level').distinct()
                research_degree_level = models.DegreeLevel.objects.filter(id__in=research_degree_level_ids).order_by(
                    'order')
                research_serializer = DegreeLevelViewSerializer(research_degree_level, many=True)

                my_list.append({'id': discipline.id, 'name': discipline.name,
                                'logo': discipline.logo, 'icon': discipline.icon,
                                'undergradute': undergradute_serializer.data,
                                'postgradute': postgradute_serializer.data,
                                'research': research_serializer.data,
                                })
            dump = json.dumps(my_list)
            cache.set(cache_id, dump, timeout=CACHE_TTL)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], url_path='institutes/rankings')
    def country_institutes_ranking(self, request, *args, **kwargs):
        """
        Returns list of institute rankings   with respect to  country`.
        """
        # order = request.GET.get('order').strip()
        # print(order)
        # models.Institute.objects.filter(instituteranking__ranking_type=)
        country_instance = self.get_object()
        qs = models.Institute.objects.filter(institutecampus__city__state__country=country_instance).order_by(
            'id').distinct()
        results = []
        for institute in qs:
            data = {
                'id': institute.id,
                'name': institute.institute_name,
                'qs_world_ranking': get_ranking(headers.QAS_WORLD_RANKING, institute),
                'times_higher_world_ranking': get_ranking(headers.TIMES_HIGHER_WORLD_RANKING, institute),
                'us_news_world_ranking': get_ranking(headers.US_NEWS_WORLD_RANKING, institute),
                'us_news_national_ranking': get_ranking(headers.US_NEWS_NATIONAL_RANKING, institute),
                'shanghai_ranking': get_ranking(headers.SHANGHAI_RANKING, institute),
                'tcf_ranking': get_ranking(headers.TCF_RANKING, institute),
            }
            results.append(data)

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

        # if order:
        #     print(qs.count())
        #     # qs = qs.order_by(
        #     #     order).distinct()
        #     qs = qs.filter(instituteranking__ranking_type='qs_world_ranking',
        #                    instituteranking__value__isnull=False).order_by('instituteranking__value').distinct()
        #     # qs =qs.order_by('instituteranking__value').distinct()
        #     # print(qs.count())
        # else:
        #     qs = qs.order_by(
        #         'institute_name').distinct()
        #
        # page = self.paginate_queryset(qs)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        #
        # serializer = self.get_serializer(qs, many=True)
        # return Response(serializer.data)

    @action(detail=True, methods=['get'], name='country_discipline_related_degree_levels',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/degree_levels')
    def country_discipline_related_degree_levels(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        country = self.get_object()
        institutes = models.Institute.objects.filter(institutecampus__city__state__country=country)
        courses = models.Course.objects.filter(campus__institute__in=institutes, discipline__id=discipline_pk)
        degree_levels = models.DegreeLevel.objects.filter(course__in=courses).annotate(
            course_count=Count('course'))
        results = []
        for degree_level in degree_levels:
            results.append(
                {'id': degree_level.id, 'name': degree_level.display_name,
                 'course_count': degree_level.course_count})

        dump = json.dumps(results)

        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='country_discipline_related_intakes',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/intakes')
    def country_discipline_related_intakes(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        country = self.get_object()
        institutes = models.Institute.objects.filter(institutecampus__city__state__country=country)
        courses = models.Course.objects.filter(campus__institute__in=institutes, discipline__id=discipline_pk)
        intakes = models.CourseIntakeAndDeadLine.objects.filter(course__in=courses).annotate(
            course_count=Count('course'))
        results = []
        for key, value in INTAKE_MONTHS:
            results.append({'month': value, 'course_count': 0})

        for intake in intakes:
            for result in results:
                if intake.intake_month == result['month']:
                    result['course_count'] = result['course_count'] + intake.course_count
        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='country_discipline_related_specializations',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/specializations')
    def country_discipline_related_specializations(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """

        country = self.get_object()
        institutes = models.Institute.objects.filter(institutecampus__city__state__country=country)
        courses = models.Course.objects.filter(campus__institute__in=institutes, discipline__id=discipline_pk)
        specializations = models.Specialization.objects.filter(course__in=courses).annotate(
            course_count=Count('course'))
        serializer = self.get_serializer(specializations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='country_discipline_related_institutes',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/institutes')
    def country_discipline_related_institutes(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """

        country = self.get_object()
        institutes = models.Institute.objects.filter(institutecampus__city__state__country=country).distinct()
        courses = models.Course.objects.filter(campus__institute__in=institutes, discipline__id=discipline_pk)
        campuses = models.InstituteCampus.objects.filter(course__in=courses).annotate(course_count=Count('course'))
        results = []
        for campus in campuses:
            item, index = next(
                ((item, index) for index, item in enumerate(results) if item['id'] == campus.institute.id),
                (None, None))
            if item:
                item['course_count'] = item['course_count'] + campus.course_count
                results[index] = item
            else:
                results.append({'id': campus.institute.id, 'name': campus.institute.institute_name,
                                'course_count': campus.course_count})

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='country_discipline_related_locations',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/locations')
    def country_discipline_related_locations(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        country = self.get_object()
        institutes = models.Institute.objects.filter(institutecampus__city__state__country=country).distinct()
        courses = models.Course.objects.filter(campus__institute__in=institutes, discipline__id=discipline_pk)
        campus_list = models.InstituteCampus.objects.filter(course__in=courses).annotate(course_count=Count('course'))
        states = set(campus_list.values_list('city__state', flat=True))
        states = models.State.objects.filter(id__in=states)
        countries = set(states.values_list('country', flat=True))
        countries = models.Country.objects.filter(id__in=countries)

        countries_list = []
        for country in countries:
            countries_list.append({'id': country.id, 'name': country.name,
                                   'course_count': 0, 'states': [],
                                   })
        states_list = []
        for state in states:
            states_list.append({'id': state.id, 'name': state.name,
                                'course_count': 0, 'cities': [],
                                'country_id': state.country.id,
                                })

        for campus in campus_list:
            for state in states_list:
                if state['id'] == campus.city.state.id:
                    state['cities'].append({'id': campus.city.id, 'name': campus.city.name,
                                            'course_count': campus.course_count,
                                            })
                    state['course_count'] = state['course_count'] + campus.course_count

        for state in states_list:
            for country in countries_list:
                if country['id'] == state['country_id']:
                    country['states'].append(state)
                    country['course_count'] = country['course_count'] + state['course_count']
        dump = json.dumps(countries_list)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], url_path='country_faqa')
    def country_faqas(self, request, *args, **kwargs):
        country = self.get_object()
        faqs = models.CountryFAQA.objects.filter(country=country)
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='countries_map', url_path='countries_map')
    def countries_map(self, request, *args, **kwargs):
        countries = models.Country.objects.all()
        serializer = self.get_serializer(countries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='states_map', url_path='states_map')
    def states_map(self, request, *args, **kwargs):
        country = self.get_object()
        states = models.State.objects.filter(country=country).annotate(campus_count=Count('city__institutecampus'))
        serializer = self.get_serializer(states, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='cities_map', url_path='state/(?P<states_pk>[0-9]+)/cities_map')
    def cities_map(self, request, states_pk, *args, **kwargs):
        cities = models.City.objects.filter(state=states_pk).annotate(campus_count=Count('institutecampus'))
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='cities_campuses_map', url_path='city/(?P<city_pk>[0-9]+)/campuses_map')
    def cities_campuses_map(self, request, city_pk, *args, **kwargs):
        campuses = models.InstituteCampus.objects.filter(city__id=city_pk)
        serializer = self.get_serializer(campuses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='state_campuses_map',
            url_path='state/(?P<state_pk>[0-9]+)/campuses_map')
    def state_campuses_map(self, request, state_pk, *args, **kwargs):
        campuses = models.InstituteCampus.objects.filter(city__state__pk=state_pk)
        serializer = self.get_serializer(campuses, many=True)
        return Response(serializer.data)


class StateViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.State.objects.all()
    serializer_classes = {
        'list': country.StateListSerializer,
        'retrieve': country.StateDetailSerializer,
        'cities': country.CityListSerializer,
        'institutes': country.InstituteListSerializer,
    }
    default_serializer_class = country.StateListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['get'], name='cities', url_path='cities')
    def cities(self, request, *args, **kwargs):
        """
        Returns  cities list by state id with count`.
        """
        state_instance = self.get_object()
        qs = models.City.objects.filter(state=state_instance).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='institutes', url_path='institutes')
    def institutes(self, request, *args, **kwargs):
        """
        Returns  institutes list by state id with count`.
        """
        state_instance = self.get_object()
        qs = models.Institute.objects.filter(institutecampus__city__state=state_instance).order_by(
            'id').distinct('id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.City.objects.all()
    serializer_classes = {
        'list': country.CityListSerializer,
        'retrieve': country.CityDetailSerializer,
        'institutes': country.InstituteListSerializer
    }
    default_serializer_class = country.StateListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['get'], name='institutes', url_path='institutes')
    def institutes(self, request, *args, **kwargs):
        """
        Returns  institutes list by country id with count`.
        """
        country_instance = self.get_object()
        qs = models.Institute.objects.filter(institutecampus__city=country_instance).order_by(
            'id').distinct('id')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
