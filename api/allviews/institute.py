import json

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Sum, Count

from constructor.choices import INTAKE_MONTHS
from constructor.paginator import ResultsSetPagination
from constructor import models
from api.serializers import institute, course, discipline
from rest_framework.response import Response
from api.serializers.degree_level import DegreeLevelViewSerializer

from django.db.models import CharField, QuerySet
from django.db.models.functions import Lower
from collections import namedtuple

CharField.register_lookup(Lower)


class InstituteViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.Institute.objects.all()
    serializer_classes = {
        'all_institutes': institute.AllInstituteRankingsSerializer,
        'list': institute.InstituteListSerializer,
        'retrieve': institute.InstituteDetailSerializer,
        'campus': institute.CampusListSerializer,
        'courses': institute.CourseListWithCampusSerializer,
        'discipline_courses': course.CourseDetailsSerializer,
        'course_related_specialization': discipline.SpecializationRelatedCourseCountSerializer,
        'institute_discipline_related_specializations': discipline.SpecializationRelatedCourseCountSerializer,
        'institute_related_specializations': discipline.SpecializationRelatedCourseCountSerializer

    }
    default_serializer_class = institute.InstituteListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='all_institutes', url_path='all')
    def all_institutes(self, request, *args, **kwargs):
        """
        Returns list of all courses`.
        """
        qs = models.Institute.objects.filter(instituteranking__ranking_type='qs_world_ranking',
                                             instituteranking__value__isnull=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='campus', url_path='campus')
    def campus(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        qs = models.InstituteCampus.objects.filter(institute=institute_instance).order_by('campus')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='courses', url_path='courses')
    def courses(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        qs = models.Course.objects.filter(campus__institute=institute_instance).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='related_discipline', url_path='related_discipline')
    def related_discipline(self, request, *args, **kwargs):
        institute_instance = self.get_object()
        disciplines = models.Discipline.objects.all()
        results = []
        for discipline in disciplines:
            results.append({'id': discipline.id, 'name': discipline.name,
                            'courses_count': models.Course.objects.filter(discipline=discipline,
                                                                          campus__institute=institute_instance).count()})
        dump = json.dumps(results)
        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['post'], name='discipline', url_path='discipline')
    def discipline(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        query_dict = {}
        institute_instance = self.get_object()
        campuses_ids = request.data.get('campuses', [])
        if len(campuses_ids):
            all_campus = institute_instance.institutecampus_set.all()
            campuses = all_campus.filter(id__in=campuses_ids)
            query_dict['campus__in'] = campuses
            print(query_dict)
        else:
            query_dict['campus__institute'] = institute_instance
        # qs = models.Course.objects.filter(campus__institute=institute_instance).order_by('name')
        courses = models.Course.objects.filter(**query_dict)
        # courses = models.Course.objects.filter(campus__institute=institute_instance).order_by('name')
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
        # serializer = self.get_serializer(qs, many=True)
        # return Response(serializer.data)

    @action(detail=True, methods=['get'], name='discipline_courses', url_path='discipline/(?P<discipline_pk>[0-9]+)')
    def discipline_courses(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        qs = models.Course.objects.filter(campus__institute=institute_instance).order_by('name')
        qs = qs.filter(discipline__id=discipline_pk)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], name='institute_discipline_related_degree_levels',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/degree_levels')
    def institute_discipline_related_degree_levels(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance, discipline__id=discipline_pk)
        degree_levels = models.DegreeLevel.objects.filter(course__in=courses).annotate(
            course_count=Count('course'))
        results = []
        for degree_level in degree_levels:
            results.append(
                {'id': degree_level.id, 'name': degree_level.display_name,
                 'course_count': degree_level.course_count})

        dump = json.dumps(results)

        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['post'], name='institute_related_degree_levels',
            url_path='degree_levels')
    def institute_related_degree_levels(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance)
        query_dict = {}
        if request.data.get('disciplines'):
            query_dict['discipline__in'] = request.data.get('disciplines')

        qs = courses.filter(**query_dict)
        degree_levels = models.DegreeLevel.objects.filter(course__in=qs).annotate(
            course_count=Count('course'))
        results = []
        for degree_level in degree_levels:
            results.append(
                {'id': degree_level.id, 'name': degree_level.display_name,
                 'course_count': degree_level.course_count})

        dump = json.dumps(results)

        return HttpResponse(dump, content_type='application/json')

    @action(detail=True, methods=['get'], name='institute_discipline_related_intakes',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/intakes')
    def institute_discipline_related_intakes(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance, discipline__id=discipline_pk)
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

    @action(detail=True, methods=['post'], name='institute_related_intakes',
            url_path='intakes')
    def institute_discipline_related_intakes(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance)
        query_dict = {}
        if request.data.get('disciplines'):
            query_dict['discipline__in'] = request.data.get('disciplines')

        qs = courses.filter(**query_dict)
        intakes = models.CourseIntakeAndDeadLine.objects.filter(course__in=qs).annotate(
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

    @action(detail=True, methods=['get'], name='institute_discipline_related_specializations',
            url_path='discipline/(?P<discipline_pk>[0-9]+)/specializations')
    def institute_discipline_related_specializations(self, request, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance, discipline__id=discipline_pk)
        specializations = models.Specialization.objects.filter(course__in=courses).annotate(
            course_count=Count('course'))
        serializer = self.get_serializer(specializations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], name='institute_related_specializations',
            url_path='specializations')
    def institute_related_specializations(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        courses = models.Course.objects.filter(campus__institute=institute_instance)
        query_dict = {}
        if request.data.get('disciplines'):
            query_dict['discipline__in'] = request.data.get('disciplines')

        qs = courses.filter(**query_dict)
        specializations = models.Specialization.objects.filter(course__in=qs).annotate(
            course_count=Count('course'))
        serializer = self.get_serializer(specializations, many=True)
        return Response(serializer.data)


class CampusViewSet(viewsets.ModelViewSet, ResultsSetPagination):
    queryset = models.InstituteCampus.objects.all()

    serializer_classes = {
        'list': institute.CampusListSerializer,
        'retrieve': institute.CampusDetailSerializer,
        'search': institute.CampusDetailSearchSerializer,
        'location': institute.CampusLocationSerializer,
        'institute_location': institute.CampusLocationSerializer,
    }
    default_serializer_class = institute.CampusListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=True, methods=['get'], name='courses', url_path='courses')
    def courses(self, request, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        institute_instance = self.get_object()
        qs = models.Course.objects.filter(campus__institute=institute_instance).order_by('name')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='search', url_path='search')
    def search(self, request, *args, **kwargs):
        """
        Returns  institutes list by params with count`.
        """
        qs = models.InstituteCampus.objects.all()
        query_dict = {}
        if len(list(filter(None, request.GET.getlist('country')))) > 0:
            query_dict['city__state__country__in'] = request.GET.get('country')
        if len(list(filter(None, request.GET.getlist('state')))) > 0:
            query_dict['city__state__in'] = request.GET.getlist('state')
        if len(list(filter(None, request.GET.getlist('city')))) > 0:
            query_dict['city__in'] = request.GET.getlist('city')
        if len(list(filter(None, request.GET.getlist('degree_level')))) > 0:
            query_dict['course__degree_level__in'] = request.GET.getlist('degree_level')
        if len(list(filter(None, request.GET.getlist('discipline')))) > 0:
            query_dict['course__discipline__in'] = request.GET.getlist('discipline')
        if request.GET.get('course'):
            query_dict['course__name__search'] = request.GET.get('course').strip()
        qs = qs.filter(**query_dict).order_by('institute__institute_name')
        if request.GET.get('course'):
            qs = qs.annotate(Count('id'))
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='location', url_path='locations')
    def location(self, request, *args, **kwargs):
        qs = models.InstituteCampus.objects.all()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='location', url_path='institute/(?P<institute_pk>[0-9]+)/locations')
    def institute_location(self, request, institute_pk, *args, **kwargs):
        qs = models.InstituteCampus.objects.filter(institute__id=institute_pk)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
