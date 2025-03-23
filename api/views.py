from rest_framework import viewsets, renderers, status
from constructor import models
from api.serializers import discipline, degree_level
from constructor.paginator import ResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db.models import Count
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class DisciplineViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Discipline.objects.all()
    serializer_classes = {
        'list': discipline.DisciplineListViewSerializer,
        'retrieve': discipline.DisciplineDetailViewSerializer,
        'specializations': discipline.SpecializationDetailViewSerializer,
        'disciplines_with_count': discipline.DisciplineWithCourseCountSerializer,
    }
    default_serializer_class = discipline.DisciplineListViewSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def list(self, request, *args, **kwargs):
        if 'disciplines' in cache:
            data = cache.get('disciplines')
            if isinstance(data, list):
                self.page = self.paginate_queryset(data)
                return self.get_paginated_response(data)
            return Response(data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set('disciplines', serializer.data, timeout=CACHE_TTL)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            cache.set('disciplines', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='disciplines_with_count')
    def disciplines_with_count(self, request, *args, **kwargs):
        qs = models.Discipline.objects.all().annotate(
            course_count=Count('course'))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='specializations')
    def specializations(self, request, *args, **kwargs):
        """
        Returns  all specializations  list`.
        """
        discipline = self.get_object()
        if request.GET.get('search'):
            qs = models.Course.objects.filter(discipline=discipline, specialization__name__icontains=request.GET.get(
                'search').strip()).values_list('specialization')
        else:
            qs = models.Course.objects.filter(discipline=discipline).values_list('specialization')
        qs = models.Specialization.objects.filter(id__in=qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'discipline_id': discipline.id,
                                                                       'discipline_name': discipline.name})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True,
                                         context={'discipline_id': discipline.id, 'discipline_name': discipline.name})
        return Response(serializer.data)

        # serializer = self.get_serializer(qs, many=True,
        #                                  context={'discipline_id': discipline.id, 'discipline_name': discipline.name})
        # return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='all')
    def all_disciplines(self, request, *args, **kwargs):
        """
        Returns list of disciplines  with respect to  country`.
        """
        courses = models.Course.objects.all().order_by('name')
        qs = courses.values('discipline').distinct()
        disciplines = models.Discipline.objects.filter(id__in=qs)
        my_list = []
        for discipline in disciplines:
            qs = courses.filter(discipline=discipline)
            undergradute_degree_level_ids = qs.filter(degree_level__level_type='undergradute').values(
                'degree_level').distinct()
            undergradute_degree_level = models.DegreeLevel.objects.filter(
                id__in=undergradute_degree_level_ids).order_by('order')
            undergradute_serializer = degree_level.DegreeLevelViewSerializer(undergradute_degree_level, many=True)

            postgradute_degree_level_ids = qs.filter(degree_level__level_type='postgradute').values(
                'degree_level').distinct()
            postgradute_degree_level = models.DegreeLevel.objects.filter(id__in=postgradute_degree_level_ids).order_by(
                'order')
            postgradute_serializer = degree_level.DegreeLevelViewSerializer(postgradute_degree_level, many=True)

            research_degree_level_ids = qs.filter(degree_level__level_type='postgradute_by_research').values(
                'degree_level').distinct()
            research_degree_level = models.DegreeLevel.objects.filter(id__in=research_degree_level_ids).order_by(
                'order')
            research_serializer = degree_level.DegreeLevelViewSerializer(research_degree_level, many=True)

            my_list.append({'id': discipline.id, 'name': discipline.name,
                            'logo': discipline.logo, 'icon': discipline.icon,
                            'undergradute': undergradute_serializer.data,
                            'postgradute': postgradute_serializer.data,
                            'research': research_serializer.data,
                            })
        dump = json.dumps(my_list)
        return HttpResponse(dump, content_type='application/json')


class DegreeLevelViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.DegreeLevel.objects.all().order_by('order')
    serializer_classes = {
        'list': degree_level.DegreeLevelViewSerializer,
        'retrieve': degree_level.DegreeLevelViewSerializer,
    }
    default_serializer_class = degree_level.DegreeLevelViewSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def list(self, request, *args, **kwargs):
        if 'degree_levels' in cache:
            data = cache.get('degree_levels')
            if isinstance(data, list):
                self.page = self.paginate_queryset(data)
                return self.get_paginated_response(data)
            return Response(data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                cache.set('degree_levels', serializer.data, timeout=CACHE_TTL)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            cache.set('degree_levels', serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)


class CourseTitleViewSet(viewsets.ModelViewSet):
    queryset = models.CourseTitle.objects.all()
    serializer_classes = {
        'list': degree_level.CourseTitlelViewSerializer,
        'retrieve': degree_level.CourseTitlelViewSerializer,
    }
    default_serializer_class = degree_level.CourseTitlelViewSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)
