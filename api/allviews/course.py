import json

from django.db.models import Count, Q
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from api.serializers import institute
from constructor.choices import INTAKE_MONTHS
from constructor.paginator import ResultsSetPagination
from constructor import models
from api.serializers import course, discipline
from rest_framework.response import Response
from api.helper import get_distance
from api.query_helper import (get_coures_query, get_filtered_courses, courses_group_by_institutes, get_search_courses,
                              apply_filter_on_courses)

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class CourseViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Course.objects.all()
    serializer_classes = {
        'all_courses': course.AllCourseSerializer,
        'list': course.CourseListSerializer,
        'retrieve': course.CourseDetailsSerializer,
        'search': course.CourseDetailsSerializer,
        'crm_course_search': course.CourseDetailsSerializer,
        'my_suggested_course_search': course.CourseCardSerializer,
        'my_suggested_course_group_search': course.CourseCardGroupSerializer,
        'courses_by_ids': course.RelatedCourseCardSerializer,
        'course_search': course.CoursesGroupSerializer,
        'search_name': course.CourseNameSerializer,
        'institute_courses': course.CourseDetailsSerializer,
        'country_courses': course.CourseDetailsSerializer,
        'course_related_specialization': discipline.SpecializationRelatedCourseCountSerializer,
        'course_compare': course.CourseCompareSerializer,
        'location_search': institute.CampusLocationSerializer,
        'crm_course_detail': course.CrmCourseDetailsSerializer,
        'course_all_locations': course.CourseAllLocationsSerializer,
        'course_related_institutes': course.CourseRelatedInstitutesSerializer,
        'course_related_campuses': course.CourseRelatedCampusesSerializer,
    }
    default_serializer_class = course.CourseListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['get'], name='crm_course_detail', url_path='crm_course_detail')
    def crm_course_detail(self, request, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        qs = self.get_object()
        serializer = self.get_serializer(qs)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='all_courses', url_path='all_courses')
    def all_courses(self, request, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        qs = models.Course.objects.all()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='courses_by_ids', url_path='courses_by_ids')
    def courses_by_ids(self, request, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        course_ids = request.data.get('courses_ids')
        if len(course_ids):
            qs = models.Course.objects.filter(pk__in=course_ids)
            page = self.paginate_queryset(qs)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=False, methods=['get'], name='search', url_path='search')
    def search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.Course.objects.all()
        query_dict = {}
        if len(list(filter(None, request.GET.getlist('country')))) > 0:
            query_dict['campus__city__state__country__in'] = request.GET.get('country')
        if len(list(filter(None, request.GET.getlist('state')))) > 0:
            query_dict['campus__city__state__in'] = request.GET.getlist('state')
        if len(list(filter(None, request.GET.getlist('city')))) > 0:
            query_dict['campus__city__in'] = request.GET.getlist('city')
        if len(list(filter(None, request.GET.getlist('degree_level')))) > 0:
            query_dict['degree_level__in'] = request.GET.getlist('degree_level')
        if len(list(filter(None, request.GET.getlist('discipline')))) > 0:
            query_dict['discipline__in'] = request.GET.getlist('discipline')
        if request.GET.get('campus'):
            query_dict['campus__id'] = request.GET.get('campus')
        if request.GET.get('course'):
            query_dict['name__search'] = request.GET.get('course').strip()

        qs = qs.filter(**query_dict).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='search_name', url_path='search_name')
    def search_name(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.Course.objects.all()
        query_dict = {}
        if request.GET.get('course'):
            query_dict['name__contains'] = request.GET.get('course').strip()
        qs = qs.filter(**query_dict).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='search_related', url_path='search_related')
    def search_related(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.Course.objects.all()
        query_dict = {}
        if request.GET.get('course'):
            query_dict['name__contains'] = request.GET.get('course').strip()
        qs = qs.filter(**query_dict).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='course_all_locations', url_path='course_all_locations')
    def course_all_locations(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        countries = models.Country.objects.all()
        serializer = self.get_serializer(countries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='course_related_locations', url_path='course_related_locations')
    def course_related_locations(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        result = None
        if request.data.get("advance"):
            if 'advance_search_countries' in cache:
                result = cache.get('advance_search_countries')
            else:
                result = self.get_course_related_countries_list(request)
                cache.set('advance_search_countries', result, timeout=CACHE_TTL)
        else:
            result = self.get_course_related_countries_list(request)

        return HttpResponse(result, content_type='application/json')

    def get_course_related_countries_list(self, request):
        # courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)
        campus_list = models.InstituteCampus.objects.filter(course__in=filtered_query_set_courses).annotate(
            course_count=Count('course'))
        states = set(campus_list.values_list('city__state', flat=True))
        states = models.State.objects.filter(id__in=states).order_by('name')
        countries = set(states.values_list('country', flat=True))
        countries = models.Country.objects.filter(id__in=countries)

        cities = []
        for campus in campus_list:
            status = True
            for city in cities:
                if campus.city.id == city['id']:
                    city['course_count'] = city['course_count'] + campus.course_count
                    status = False
                    break
            if status:
                cities.append({'id': campus.city.id, 'name': campus.city.name,
                               'course_count': campus.course_count, 'state_id': campus.city.state.id,
                               'country_id': campus.city.state.country.id
                               })
        cities = sorted(cities, key=lambda i: i['name'])
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

        for city in cities:
            for state in states_list:
                if state['id'] == city['state_id']:
                    state['cities'].append(city)
                    state['course_count'] = state['course_count'] + city['course_count']

        for state in states_list:
            for country in countries_list:
                if country['id'] == state['country_id']:
                    country['states'].append(state)
                    country['course_count'] = country['course_count'] + state['course_count']
        return json.dumps(countries_list)

    @action(detail=False, methods=['post'], name='course_related_institutes', url_path='course_related_institutes')
    def course_related_institutes(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """

        # name = request.data.get("course").strip()
        # courses = models.Course.objects.filter(name__search=name)
        # if courses.count() == 0:
        #     courses = models.Course.objects.filter(specialization__name__search=name)
        #     if courses.count() == 0:
        #         courses = models.Course.objects.filter(discipline__name__search=name)
        # qs = get_coures_query(request.data.get("course"))
        #
        # query_dict = {}
        #
        # if request.data.get("countries"):
        #     query_dict['campus__city__state__country__in'] = request.data.get("countries")
        # if request.data.get("states"):
        #     query_dict['campus__city__state__in'] = request.data.get("states")
        # if request.data.get("cities"):
        #     query_dict['campus__city__in'] = request.data.get("cities")
        # if request.data.get("degree_levels"):
        #     query_dict['degree_level__in'] = request.data.get("degree_levels")
        # if request.data.get("disciplines"):
        #     query_dict['discipline__in'] = request.data.get("disciplines")
        # if request.data.get("specializations"):
        #     query_dict['specialization__in'] = request.data.get("specializations")
        #
        # courses = qs.filter(**query_dict)

        # courses = get_filtered_courses(request)

        # institutes_list = []
        # campus_list = models.InstituteCampus.objects.filter(course__in=courses).annotate(course_count=Count('course'))
        # institutes_ids = set(campus_list.values_list('institute', flat=True))
        # institutes = models.Institute.objects.filter(id__in=institutes_ids).order_by('institute_name')
        # for institute in institutes:
        #     institutes_list.append({'id': institute.id, 'name': institute.institute_name,
        #                             'course_count': 0
        #                             })
        # for campus in campus_list:
        #     for institute in institutes_list:
        #         if institute['id'] == campus.institute.id:
        #             institute['course_count'] = institute['course_count'] + campus.course_count
        #
        # dump = json.dumps(institutes_list)
        # return HttpResponse(dump, content_type='application/json')
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)
        if request.GET.get('search'):
            # institutes = models.Institute.objects.filter(institutecampus__course__in=courses,
            #                                              institute_name__istartswith=request.GET.get(
            #                                                  'search').strip()).annotate(
            #     course_count=Count('institutecampus__course')).order_by('institute_name')
            # if institutes.count() == 0:
            institutes = models.Institute.objects.filter(institutecampus__course__in=filtered_query_set_courses,
                                                         institute_name__icontains=request.GET.get(
                                                             'search').strip()).annotate(
                course_count=Count('institutecampus__course')).order_by('institute_name')

        else:
            institutes = models.Institute.objects.filter(
                institutecampus__course__in=filtered_query_set_courses).annotate(
                course_count=Count('institutecampus__course')).order_by('institute_name')

        page = self.paginate_queryset(institutes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='course_related_campuses', url_path='course_related_campuses')
    def course_related_campuses(self, request, *args, **kwargs):
        results = []
        if request.data.get("institutes"):
            query_set_courses = get_search_courses(request)
            filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)
            all_campuses = models.InstituteCampus.objects.filter(institute__in=request.data.get("institutes"))
            filter_campuses = all_campuses.filter(course__in=filtered_query_set_courses).annotate(
                course_count=Count('course')).order_by('campus')
            results = []
            for campus in all_campuses:
                results.append(
                    {'id': campus.id, 'name': campus.campus + ' ( ' + campus.city.name + ' )', 'course_count': 0})
            for result in results:
                for filter_campus in filter_campuses:
                    if filter_campus.id == result['id']:
                        result['course_count'] = filter_campus.course_count

        # serializer = self.get_serializer(qs, many=True)
        # return Response(serializer.data)
        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='course_related_degree_levels',
            url_path='course_related_degree_levels')
    def course_related_degree_levels(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        # qs = get_coures_query_test(request.data.getlist("course"))
        # name = request.data.get("course").strip()

        # courses = models.Course.objects.filter(name__search=name)
        # if courses.count() == 0:
        #     courses = models.Course.objects.filter(specialization__name__search=name)
        #     if courses.count() == 0:
        #         courses = models.Course.objects.filter(discipline__name__search=name)

        # query_dict = {}
        #
        # if request.data.get("countries"):
        #     query_dict['campus__city__state__country__in'] = request.data.get("countries")
        # if request.data.get("states"):
        #     query_dict['campus__city__state__in'] = request.data.get("states")
        # if request.data.get("cities"):
        #     query_dict['campus__city__in'] = request.data.get("cities")
        # if request.data.get("specializations"):
        #     query_dict['specialization__in'] = request.data.get("specializations")
        #
        # courses = qs.filter(**query_dict)

        # courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)

        degree_levels = models.DegreeLevel.objects.filter(course__in=filtered_query_set_courses).annotate(
            course_count=Count('course'))

        results = [
            {'id': 1, 'name': 'Undergradute', 'type': 'undergradute', 'course_count': 0, 'degree_levels': []},
            {'id': 2, 'name': 'Postgradute', 'type': 'postgradute', 'course_count': 0, 'degree_levels': []},
            {'id': 3, 'name': 'Postgradute by Research', 'type': 'postgradute_by_research', 'course_count': 0,
             'degree_levels': []},
        ]
        degree_levels_list = models.DegreeLevel.objects.all().order_by('order')
        for degree_level in degree_levels_list.filter(level_type='undergradute'):
            results[0]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'course_count': 0,
                                                })

        for degree_level in degree_levels_list.filter(level_type='postgradute'):
            results[1]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'course_count': 0,
                                                })
        for degree_level in degree_levels_list.filter(level_type='postgradute_by_research'):
            results[2]['degree_levels'].append({'id': degree_level.id, 'name': degree_level.display_name,
                                                'course_count': 0,
                                                })

        for degree_level in degree_levels:
            if degree_level.level_type == 'undergradute':
                for index, obj in enumerate(results[0]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[0]['degree_levels'][index]['course_count'] = degree_level.course_count
                results[0]['course_count'] = results[0]['course_count'] + degree_level.course_count
            if degree_level.level_type == 'postgradute':
                for index, obj in enumerate(results[1]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[1]['degree_levels'][index]['course_count'] = degree_level.course_count
                results[1]['course_count'] = results[1]['course_count'] + degree_level.course_count
            if degree_level.level_type == 'postgradute_by_research':
                for index, obj in enumerate(results[2]['degree_levels']):
                    if obj['id'] == degree_level.id:
                        results[2]['degree_levels'][index]['course_count'] = degree_level.course_count
                results[2]['course_count'] = results[2]['course_count'] + degree_level.course_count

        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='course_related_disciplines',
            url_path='course_related_disciplines')
    def course_related_disciplines(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        # courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)
        coures_ids = filtered_query_set_courses.values_list('id', flat=True)
        results = []
        disciplines = models.Discipline.objects.all().order_by('name')
        for discipline in disciplines:
            results.append({'id': discipline.id, 'name': discipline.name,
                            'courses_count': models.Discipline.objects.filter(id=discipline.id,
                                                                              course__in=coures_ids).count()})
        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='course_related_specialization',
            url_path='course_related_specialization')
    def course_related_specialization(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        # name = request.data.get("course").strip()
        # qs = get_coures_query(request.data.get("course"))

        # courses = models.Course.objects.filter(name__search=name)
        # if courses.count() == 0:
        #     courses = models.Course.objects.filter(specialization__name__search=name)
        #     if courses.count() == 0:
        #         courses = models.Course.objects.filter(discipline__name__search=name)

        # query_dict = {}
        #
        # if request.data.get("countries"):
        #     query_dict['campus__city__state__country__in'] = request.data.get("countries")
        # if request.data.get("states"):
        #     query_dict['campus__city__state__in'] = request.data.get("states")
        # if request.data.get("cities"):
        #     query_dict['campus__city__in'] = request.data.get("cities")
        # if request.data.get("degree_levels"):
        #     query_dict['degree_level__in'] = request.data.get("degree_levels")
        # if request.data.get("disciplines"):
        #     query_dict['discipline__in'] = request.data.get("disciplines")
        # if request.data.get("institute_type"):
        #     query_dict['campus__institute__institute_type__in'] = request.data.get("institute_type")
        # if request.data.get("specializations"):
        #     query_dict['specialization__in'] = request.data.get("specializations")
        #
        # courses = qs.filter(**query_dict)
        # courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)

        if request.GET.get('search'):
            # specializations = models.Specialization.objects.filter(course__in=courses,
            #                                                        name__istartswith=request.GET.get(
            #                                                            "search").strip()).annotate(
            #     course_count=Count('course')).order_by('name')
            # if specializations.count() == 0:
            specializations = models.Specialization.objects.filter(course__in=filtered_query_set_courses,
                                                                   name__icontains=request.GET.get(
                                                                       "search").strip()).annotate(
                course_count=Count('course')).order_by('name')

        else:
            specializations = models.Specialization.objects.filter(course__in=filtered_query_set_courses).annotate(
                course_count=Count('course')).order_by('name')

        page = self.paginate_queryset(specializations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

        # serializer = self.get_serializer(specializations, many=True)
        # return Response(serializer.data)

    @action(detail=False, methods=['post'], name='course_related_intakes',
            url_path='course_related_intakes')
    def course_related_intakes(self, request, *args, **kwargs):
        """
        Returns  months list by params with course  count`.
        """
        # courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)

        intakes = models.CourseIntakeAndDeadLine.objects.filter(course__in=filtered_query_set_courses).annotate(
            course_count=Count('course'))
        results = []
        for key, value in INTAKE_MONTHS:
            results.append({'month': value, 'course_count': 0})

        for intake in intakes:
            for result in results:
                if intake.intake_month == result['month']:
                    result['course_count'] = result['course_count'] + intake.course_count
        marge_result = [
            {'key': 'Jan, Feb, Mar', 'value': [results[0], results[1], results[2]],
             'course_count': results[0]['course_count'] + results[1]['course_count'] + results[2]['course_count']},
            {'key': 'Apr, May, Jun', 'value': [results[3], results[4], results[5]],
             'course_count': results[3]['course_count'] + results[4]['course_count'] + results[5]['course_count']},
            {'key': 'Jul, Aug, Sep', 'value': [results[6], results[7], results[8]],
             'course_count': results[6]['course_count'] + results[7]['course_count'] + results[8]['course_count']},
            {'key': 'Oct, Nov, Dec', 'value': [results[9], results[10], results[11]],
             'course_count': results[9]['course_count'] + results[10]['course_count'] + results[11]['course_count']
             },
        ]
        dump = json.dumps(marge_result)
        return HttpResponse(dump, content_type='application/json')

    # @action(detail=False, methods=['post'], name='course_search', url_path='course_search')
    # def course_search(self, request, *args, **kwargs):
    #     """
    #     Returns  institutes list by params with count`.
    #     """
    #     results = courses_group_by_institutes(get_filtered_courses(request))
    #
    #     page = self.paginate_queryset(results)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(results, many=True)
    #     return Response(serializer.data)
    #  old
    @action(detail=False, methods=['post'], name='course_search', url_path='course_search')
    def my_suggested_course_search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        # filtered_query_set_courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)

        page = self.paginate_queryset(filtered_query_set_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(filtered_query_set_courses, many=True)
        return Response(serializer.data)

    # new
    @action(detail=False, methods=['post'], name='course_group_search', url_path='course_group_search')
    def my_suggested_course_group_search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        # filtered_query_set_courses = get_filtered_courses(request)
        query_set_courses = get_search_courses(request)
        filtered_query_set_courses = apply_filter_on_courses(request, query_set_courses)
        count = filtered_query_set_courses.count()
        #  new
        filtered_query_set_courses = filtered_query_set_courses.order_by('campus__id').distinct('campus__id')

        page = self.paginate_queryset(filtered_query_set_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'courses': filtered_query_set_courses})
            response = self.get_paginated_response(serializer.data)
            response.data['courses_count'] = count
            return response
            # return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(filtered_query_set_courses, many=True,
                                         context={'courses': filtered_query_set_courses})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='crm_course_search', url_path='crm_course_search')
    def crm_course_search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.Course.objects.all()
        query_dict = {}
        if request.data.get("course"):
            qs = get_coures_query(request.data.get("course").strip())
        if request.data.get("google_location"):
            google_location = request.data.get("google_location")
            distance = google_location.get("distance")
            latitude = google_location.get("latitude")
            longitude = google_location.get("longitude")
            d = get_distance(latitude, longitude)
            camp_qs = models.InstituteCampus.objects.annotate(distance=d).order_by('distance').filter(
                distance__lt=distance)
            campus_list = list(camp_qs.filter().values_list('id'))
            qs = qs.filter(campus__in=campus_list)
        if request.data.get("regions"):
            query_dict['campus__city__state__country__region__in'] = request.data.get("regions")
        if request.data.get("countries"):
            query_dict['campus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("states"):
            query_dict['campus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['campus__city__in'] = request.data.get("cities")
        if request.data.get("degree_levels"):
            query_dict['degree_level__in'] = request.data.get("degree_levels")
        if request.data.get("degree_levels_types"):
            query_dict['degree_level__level_type__in'] = request.data.get("degree_levels_types")
        if request.data.get("disciplines"):
            query_dict['discipline__in'] = request.data.get("disciplines")
        if request.data.get("institute_type"):
            query_dict['campus__institute__institute_type__in'] = request.data.get("institute_type")
        if request.data.get("specializations"):
            query_dict['specialization__in'] = request.data.get("specializations")
        if request.data.get("intakes"):
            query_dict['courseintakeanddeadline__intake_month__in'] = request.data.get("intakes")
        if request.data.get("fees"):
            query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
        if request.data.get("institutes"):
            query_dict['campus__institute__in'] = request.data.get("institutes")
        if request.data.get("panels"):
            query_dict['campus__institute__institute_panel__in'] = request.data.get("panels")

        qs = qs.filter(**query_dict)

        if request.data.get("durations"):
            qs = qs.filter(
                Q(courseduration__duration_one__range=request.data.get("durations")) |
                Q(courseduration__duration_two__range=request.data.get("durations")) |
                Q(courseduration__duration_three__range=request.data.get("durations")))

        if request.data.get("order"):
            order = request.data.get("order")
            if order == 0:
                qs = qs.order_by('name')
            if order == 1:
                qs = qs.order_by('coursefee__ceil_value')
            if order == 2:
                qs = qs.order_by('coursefee__floor_value')
            if order == 3:
                qs = qs.order_by('campus__institute__institute_panel')
            if order == 4:
                qs = qs.order_by('courseduration__duration_one')

        else:
            qs = qs.order_by('name')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='location_search', url_path='location_search')
    def location_search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.Course.objects.all()
        query_dict = {}
        if request.data.get("course"):
            qs = models.Course.objects.filter(name__search=request.data.get("course").strip())
            if qs.count() == 0:
                qs = models.Course.objects.filter(specialization__name__search=request.data.get("course").strip())
                if qs.count() == 0:
                    qs = models.Course.objects.filter(discipline__name__search=request.data.get("course").strip())

        if request.data.get("countries"):
            query_dict['campus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("states"):
            query_dict['campus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['campus__city__in'] = request.data.get("cities")
        if request.data.get("degree_levels"):
            query_dict['degree_level__in'] = request.data.get("degree_levels")
        if request.data.get("disciplines"):
            query_dict['discipline__in'] = request.data.get("disciplines")
        if request.data.get("institute_type"):
            query_dict['campus__institute__institute_type__in'] = request.data.get("institute_type")
        if request.data.get("specializations"):
            query_dict['specialization__in'] = request.data.get("specializations")
        if request.data.get("intakes"):
            query_dict['courseintakeanddeadline__intake_month__in'] = request.data.get("intakes")
        if request.data.get("fees"):
            query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
        if request.data.get("institutes"):
            query_dict['campus__institute__in'] = request.data.get("institutes")
        if request.data.get("panels"):
            query_dict['campus__institute__institute_panel__in'] = request.data.get("panels")

        qs = qs.filter(**query_dict)

        if request.data.get("durations"):
            qs = qs.filter(
                Q(courseduration__duration_one__range=request.data.get("durations")) |
                Q(courseduration__duration_two__range=request.data.get("durations")) |
                Q(courseduration__duration_three__range=request.data.get("durations")))

        if request.data.get("order"):
            order = request.data.get("order")
            if order == 0:
                qs = qs.order_by('name')
            if order == 1:
                qs = qs.order_by('coursefee__ceil_value')
            if order == 2:
                qs = qs.order_by('coursefee__floor_value')
            if order == 3:
                qs = qs.order_by('campus__institute__institute_panel')
            if order == 4:
                qs = qs.order_by('courseduration__duration_one')

        else:
            qs = qs.order_by('name')

        campuses = list(set(qs.values_list('campus', flat=True)))
        qs = models.InstituteCampus.objects.filter(id__in=campuses)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='institute_courses',
            url_path='institute/(?P<institute_pk>[0-9]+)')
    def institute_courses(self, request, institute_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        query_dict = {}
        institute_instance = get_object_or_404(models.Institute, pk=institute_pk)
        query_dict['campus__institute'] = institute_instance
        if request.data.get('disciplines'):
            query_dict['discipline__in'] = request.data.get('disciplines')
        if request.data.get('degree_levels'):
            query_dict['degree_level__in'] = request.data.get('degree_levels')
        if request.data.get("fees"):
            query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
        if request.data.get("intakes"):
            query_dict['courseintakeanddeadline__intake_month__in'] = request.data.get("intakes")
        if request.data.get("specializations"):
            query_dict['specialization__in'] = request.data.get("specializations")

        qs = models.Course.objects.filter(**query_dict)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='country_courses',
            url_path='country-courses/(?P<country_pk>[0-9]+)')
    def country_courses(self, request, country_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        country_instance = get_object_or_404(models.Country, pk=country_pk)
        query_dict = {'campus__city__state__country': country_instance}
        if request.data.get("states"):
            query_dict['campus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['campus__city__in'] = request.data.get("cities")
        if request.data.get('disciplines'):
            query_dict['discipline__in'] = request.data.get('disciplines')
        if request.data.get('degree_levels'):
            query_dict['degree_level__in'] = request.data.get('degree_levels')
        if request.data.get("fees"):
            query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
        if request.data.get("intakes"):
            query_dict['courseintakeanddeadline__intake_month__in'] = request.data.get("intakes")
        if request.data.get("specializations"):
            query_dict['specialization__in'] = request.data.get("specializations")
        if request.data.get("course"):
            query_dict['name__search'] = request.data.get("course").strip()
        if request.data.get("institutes"):
            query_dict['campus__institute__in'] = request.data.get("institutes")

        qs = models.Course.objects.filter(**query_dict)
        if request.data.get("order"):
            order = request.data.get("order")
            if order == 0:
                qs = qs.order_by('name')
            if order == 1:
                qs = qs.order_by('coursefee__ceil_value')
            if order == 2:
                qs = qs.order_by('coursefee__floor_value')
            if order == 3:
                qs = qs.order_by('campus__institute__institute_panel')
            if order == 4:
                qs = qs.order_by('courseduration__duration_one')

        else:
            qs = qs.order_by('name')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='course_compare',
            url_path='course_compare')
    def course_compare(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        course = self.get_object()
        serializer = self.get_serializer(course)
        return Response(serializer.data)
