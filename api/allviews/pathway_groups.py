import json

from django.db.models import Count
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from constructor.paginator import ResultsSetPagination
from constructor import models
from api.serializers import pathway_group
from rest_framework.response import Response
from api.serializers.degree_level import DegreeLevelViewSerializer
from api.serializers.scholarship import ScholarshipListSerializer, ScholarshipDetailSerializer
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class PathwayGroupView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.PathwayGroup.objects.all().order_by('order')
    serializer_classes = {
        'list': pathway_group.PathwayGroupListSerializer,
        'retrieve': pathway_group.PathwayGroupDetailSerializer,
        'universities': pathway_group.InstituteGroupWithUniversitiesSerializer,
        'pathway_group_scholarships': ScholarshipDetailSerializer,
        'pathway_group_courses': pathway_group.InstituteGroupCourseDetailsSerializer,

    }
    default_serializer_class = pathway_group.PathwayGroupListSerializer
    pagination_class = ResultsSetPagination

    def list(self, request, *args, **kwargs):
        if 'pathway-groups' in cache:
            data = cache.get('pathway-groups')
            if isinstance(data, list):
                self.page=self.paginate_queryset(data)
                return self.get_paginated_response(data)
            return Response(data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set('pathway-groups', serializer.data, timeout=CACHE_TTL)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            cache.set('pathway-groups', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['post'], name='universities', url_path='universities')
    def universities(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """
        pathway_group = self.get_object()
        query_dict = {'pathway_group': pathway_group}
        if request.data.get("countries"):
            query_dict['institutecampus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("institute_type"):
            query_dict['institute_type__in'] = request.data.get("institute_type")
        if request.data.get("states"):
            query_dict['institutecampus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['institutecampus__city__in'] = request.data.get("cities")

        qs = models.Institute.objects.filter(**query_dict).order_by('id').distinct('id')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='related_locations', url_path='related_locations')
    def related_locations(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """

        pathway_group = self.get_object()
        campus_list = models.InstituteCampus.objects.filter(institute__pathway_group=pathway_group).annotate(
            institute_count=Count('institute'))

        states = set(campus_list.values_list('city__state', flat=True))
        states = models.State.objects.filter(id__in=states)
        countries = set(states.values_list('country', flat=True))
        countries = models.Country.objects.filter(id__in=countries)

        countries_list = []
        for country in countries:
            countries_list.append({'id': country.id, 'name': country.name,
                                   'institute_count': 0, 'states': [],
                                   })
        states_list = []
        for state in states:
            states_list.append({'id': state.id, 'name': state.name,
                                'institute_count': 0, 'cities': [],
                                'country_id': state.country.id,
                                })

        for campus in campus_list:
            for state in states_list:
                if state['id'] == campus.city.state.id:
                    state['cities'].append({'id': campus.city.id, 'name': campus.city.name,
                                            'institute_count': campus.institute_count,
                                            })
                    state['institute_count'] = state['institute_count'] + campus.institute_count

        for state in states_list:
            for country in countries_list:
                if country['id'] == state['country_id']:
                    country['states'].append(state)
                    country['institute_count'] = country['institute_count'] + state['institute_count']

        dump = json.dumps(countries_list)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='disciplines', url_path='disciplines')
    def pathway_group_disciplines(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        # institute_groups = models.PathwayGroup.objects.all().values_list('id', flat=True)
        courses = models.Course.objects.filter(campus__institute__pathway_group__isnull=False).order_by('name')
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
            postgradute_degree_level = models.DegreeLevel.objects.filter(id__in=postgradute_degree_level_ids).order_by(
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
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='scholarships', url_path='scholarships')
    def pathway_group_scholarships(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """
        pathway_group = self.get_object()
        institutes = models.Institute.objects.filter(pathway_group=pathway_group)
        scholarships = models.Scholarship.objects.filter(institute__in=institutes)
        serializer = self.get_serializer(scholarships, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='courses', url_path='courses')
    def pathway_group_courses(self, request, *args, **kwargs):
        if request.data.get("groups"):
            qs = models.Course.objects.filter(campus__institute__pathway_group__in=request.data.get("groups"))
        else:
            qs = models.Course.objects.filter(campus__institute__pathway_group__isnull=False)
        query_dict = {}
        if request.data.get("course"):
            qs = qs.filter(name__search=request.data.get("course").strip())
            if qs.count() == 0:
                qs = qs.filter(specialization__name__search=request.data.get("course").strip())
                if qs.count() == 0:
                    qs = qs.filter(discipline__name__search=request.data.get("course").strip())

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

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # @action(detail=True, methods=['get'], name='states', url_path='states')
    # def states(self, request, *args, **kwargs):
    #     """
    #     Returns  states list by country id with count`.
    #     """
    #     qs = self.get_object()
    #     serializer = self.get_serializer(qs)
    #     return Response(serializer.data)


class InstituteGroupView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.InstituteGroup.objects.all().order_by('order')
    serializer_classes = {
        'list': pathway_group.InstituteGroupListSerializer,
        'retrieve': pathway_group.InstituteGroupDetailSerializer,
        'universities': pathway_group.InstituteGroupWithUniversitiesSerializer,
        'institute_group_universities': pathway_group.InstituteGroupWithUniversitiesListSerializer,
        'institute_group_courses': pathway_group.InstituteGroupCourseDetailsSerializer,
        'institute_group_scholarships': ScholarshipDetailSerializer
    }
    default_serializer_class = pathway_group.PathwayGroupListSerializer
    pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def list(self, request, *args, **kwargs):
        if 'institute-groups' in cache:
            data = cache.get('institute-groups')
            if isinstance(data, list):
                self.page = self.paginate_queryset(data)
                return self.get_paginated_response(data)
            return Response(data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set('institute-groups', serializer.data, timeout=CACHE_TTL)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            cache.set('institute-groups', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)


    @action(detail=True, methods=['post'], name='universities', url_path='universities')
    def universities(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """
        institute_group = self.get_object()
        query_dict = {'institute_group': institute_group}
        if request.data.get("countries"):
            query_dict['institutecampus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("institute_type"):
            query_dict['institute_type__in'] = request.data.get("institute_type")
        if request.data.get("states"):
            query_dict['institutecampus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['institutecampus__city__in'] = request.data.get("cities")

        qs = models.Institute.objects.filter(**query_dict).order_by('id').distinct('id')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='universities', url_path='universities')
    def institute_group_universities(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """
        institute_groups = models.InstituteGroup.objects.all().values_list('id', flat=True)
        query_dict = {'institute_group__in': list(institute_groups)}
        if request.data.get("countries"):
            query_dict['institutecampus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("institute_type"):
            query_dict['institute_type__in'] = request.data.get("institute_type")
        if request.data.get("states"):
            query_dict['institutecampus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['institutecampus__city__in'] = request.data.get("cities")

        qs = models.Institute.objects.filter(**query_dict).order_by('id').distinct('id')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='disciplines', url_path='disciplines')
    def institute_groups_disciplines(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_groups = models.InstituteGroup.objects.all().values_list('id', flat=True)
        courses = models.Course.objects.filter(campus__institute__institute_group__in=institute_groups).order_by('name')
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
            postgradute_degree_level = models.DegreeLevel.objects.filter(id__in=postgradute_degree_level_ids).order_by(
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
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='disciplines', url_path='disciplines')
    def institute_group_disciplines(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_group = self.get_object()
        courses = models.Course.objects.filter(campus__institute__institute_group=institute_group).order_by('name')
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
            postgradute_degree_level = models.DegreeLevel.objects.filter(id__in=postgradute_degree_level_ids).order_by(
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
        return HttpResponse(dump, content_type='application/json')

    @action(detail=False, methods=['post'], name='courses', url_path='courses')
    def institute_group_courses(self, request, *args, **kwargs):
        if request.data.get("groups"):
            qs = models.Course.objects.filter(campus__institute__institute_group__in=request.data.get("groups"))
        else:
            qs = models.Course.objects.filter(campus__institute__institute_group__isnull=False)
        query_dict = {}
        if request.data.get("course"):
            qs = qs.filter(name__search=request.data.get("course").strip())
            if qs.count() == 0:
                qs = qs.filter(specialization__name__search=request.data.get("course").strip())
                if qs.count() == 0:
                    qs = qs.filter(discipline__name__search=request.data.get("course").strip())

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

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='scholarships', url_path='scholarships')
    def institute_group_scholarships(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """
        institute_group = self.get_object()
        institutes = models.Institute.objects.filter(institute_group=institute_group)
        scholarships = models.Scholarship.objects.filter(institute__in=institutes)
        serializer = self.get_serializer(scholarships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='related_locations', url_path='related_locations')
    def related_locations(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """

        institute_group = self.get_object()
        campus_list = models.InstituteCampus.objects.filter(institute__institute_group=institute_group).annotate(
            institute_count=Count('institute'))

        states = set(campus_list.values_list('city__state', flat=True))
        states = models.State.objects.filter(id__in=states)
        countries = set(states.values_list('country', flat=True))
        countries = models.Country.objects.filter(id__in=countries)

        countries_list = []
        for country in countries:
            countries_list.append({'id': country.id, 'name': country.name,
                                   'institute_count': 0, 'states': [],
                                   })
        states_list = []
        for state in states:
            states_list.append({'id': state.id, 'name': state.name,
                                'institute_count': 0, 'cities': [],
                                'country_id': state.country.id,
                                })

        for campus in campus_list:
            for state in states_list:
                if state['id'] == campus.city.state.id:
                    state['cities'].append({'id': campus.city.id, 'name': campus.city.name,
                                            'institute_count': campus.institute_count,
                                            })
                    state['institute_count'] = state['institute_count'] + campus.institute_count

        for state in states_list:
            for country in countries_list:
                if country['id'] == state['country_id']:
                    country['states'].append(state)
                    country['institute_count'] = country['institute_count'] + state['institute_count']

        dump = json.dumps(countries_list)
        return HttpResponse(dump, content_type='application/json')


class ApplyPortalView(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.ApplyPortal.objects.all().order_by('order')
    serializer_classes = {
        'list': pathway_group.ApplyPortalSerializer,
        'retrieve': pathway_group.ApplyPortalSerializer,
        'universities': pathway_group.InstituteGroupWithUniversitiesSerializer,
    }
    default_serializer_class = pathway_group.ApplyPortalSerializer
    pagination_class = ResultsSetPagination



    def list(self, request, *args, **kwargs):
        if 'apply-portals' in cache:
            data = cache.get('apply-portals')
            if isinstance(data, list):
                self.page = self.paginate_queryset(data)
                return self.get_paginated_response(data)
            return Response(data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set('apply-portals', serializer.data, timeout=CACHE_TTL)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            cache.set('apply-portals', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['post'], name='universities', url_path='universities')
    def universities(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """

        apply_portal = self.get_object()
        query_dict = {'apply_portal': apply_portal}
        if request.data.get("countries"):
            query_dict['institutecampus__city__state__country__in'] = request.data.get("countries")
        if request.data.get("institute_type"):
            query_dict['institute_type__in'] = request.data.get("institute_type")
        if request.data.get("states"):
            query_dict['institutecampus__city__state__in'] = request.data.get("states")
        if request.data.get("cities"):
            query_dict['institutecampus__city__in'] = request.data.get("cities")

        qs = models.Institute.objects.filter(**query_dict).order_by('id').distinct('id')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='related_locations', url_path='related_locations')
    def related_locations(self, request, *args, **kwargs):
        """
        Returns  universities list by group id with count`.
        """

        apply_portal = self.get_object()
        campus_list = models.InstituteCampus.objects.filter(institute__apply_portal=apply_portal).annotate(
            institute_count=Count('institute'))

        states = set(campus_list.values_list('city__state', flat=True))
        states = models.State.objects.filter(id__in=states)
        countries = set(states.values_list('country', flat=True))
        countries = models.Country.objects.filter(id__in=countries)

        countries_list = []
        for country in countries:
            countries_list.append({'id': country.id, 'name': country.name,
                                   'institute_count': 0, 'states': [],
                                   })
        states_list = []
        for state in states:
            states_list.append({'id': state.id, 'name': state.name,
                                'institute_count': 0, 'cities': [],
                                'country_id': state.country.id,
                                })

        for campus in campus_list:
            for state in states_list:
                if state['id'] == campus.city.state.id:
                    state['cities'].append({'id': campus.city.id, 'name': campus.city.name,
                                            'institute_count': campus.institute_count,
                                            })
                    state['institute_count'] = state['institute_count'] + campus.institute_count

        for state in states_list:
            for country in countries_list:
                if country['id'] == state['country_id']:
                    country['states'].append(state)
                    country['institute_count'] = country['institute_count'] + state['institute_count']

        dump = json.dumps(countries_list)
        return HttpResponse(dump, content_type='application/json')
