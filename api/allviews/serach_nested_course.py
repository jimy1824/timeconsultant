from rest_framework import viewsets
from constructor import models
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers.serach_nested_course_serializer import CountryListSerializer, DisciplineListSerializer, \
    DegreeLevelListSerializer, SpecializationListSerializer, CourseListSerializer
from api.serializers.institute import CampusListSerializer


class SearchNestedCourseView(viewsets.ModelViewSet):
    queryset = models.Country.objects.all()
    serializer_classes = {
        'list': CountryListSerializer,
        'retrieve': CountryListSerializer,
    }
    default_serializer_class = CountryListSerializer

    # pagination_class = ResultsSetPagination

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=['get'], name='countries', url_path='countries')
    def countries(self, request, *args, **kwargs):
        countries = models.Country.objects.all().order_by('name')
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country', url_path='country/(?P<country_pk>[0-9]+)/disciplines')
    def disciplines(self, request, country_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        country = models.Country.objects.filter(id=country_pk).first()
        courses = models.Course.objects.filter(campus__city__state__country=country)
        disciplines = models.Discipline.objects.filter(course__in=courses).order_by('id').distinct('id')
        serializer = DisciplineListSerializer(disciplines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country', url_path='country/(?P<country_pk>[0-9]+)/discipline/('
                                                                    '?P<discipline_pk>[0-9]+)/degree_levels')
    def degree_level(self, request, country_pk, discipline_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        courses = models.Course.objects.filter(campus__city__state__country__id=country_pk,
                                               discipline__id=discipline_pk)
        degree_levels = models.DegreeLevel.objects.filter(course__in=courses).order_by('id').distinct('id')
        serializer = DegreeLevelListSerializer(degree_levels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country', url_path='country/(?P<country_pk>[0-9]+)/discipline/('
                                                                    '?P<discipline_pk>[0-9]+)/degree_level/('
                                                                    '?P<degree_level_pk>[0-9]+)/campuses')
    def institutes(self, request, country_pk, discipline_pk, degree_level_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        courses = models.Course.objects.filter(campus__city__state__country__id=country_pk,
                                               discipline__id=discipline_pk, degree_level__id=degree_level_pk)
        institutes = models.InstituteCampus.objects.filter(course__in=courses).order_by('id').distinct('id')
        serializer = CampusListSerializer(institutes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country', url_path='country/(?P<country_pk>[0-9]+)/discipline/('
                                                                    '?P<discipline_pk>[0-9]+)/degree_level/'
                                                                    '(?P<degree_level_pk>[0-9]+)/'
                                                                    'campus/(?P<campus_pk>[0-9]+)/specializations')
    def specialization(self, request, country_pk, discipline_pk, degree_level_pk, campus_pk, *args, **kwargs):
        """
        Returns  campus list by params with count`.
        """
        courses = models.Course.objects.filter(campus__city__state__country__id=country_pk,
                                               discipline__id=discipline_pk, degree_level__id=degree_level_pk,
                                               campus__id=campus_pk)
        degree_levels = models.Specialization.objects.filter(course__in=courses).order_by('id').distinct('id')
        serializer = SpecializationListSerializer(degree_levels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], name='country', url_path='country/(?P<country_pk>[0-9]+)/discipline/('
                                                                    '?P<discipline_pk>[0-9]+)/degree_level/'
                                                                    '(?P<degree_level_pk>[0-9]+)/campus/('
                                                                    '?P<campus_pk>[0-9]+)/'
                                                                    'specialization/(?P<specialization_pk>['
                                                                    '0-9]+)/courses')
    def courses(self, request, country_pk, discipline_pk, degree_level_pk, campus_pk, specialization_pk, *args,
                **kwargs):
        """
        Returns  campus list by params with count`.
        """
        courses = models.Course.objects.filter(campus__city__state__country__id=country_pk,
                                               discipline__id=discipline_pk, degree_level__id=degree_level_pk,
                                               specialization__id=specialization_pk,
                                               campus__id=campus_pk
                                               )
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)
