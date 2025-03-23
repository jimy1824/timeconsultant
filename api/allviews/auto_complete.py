from rest_framework import serializers
from itertools import chain
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
from rest_framework import serializers, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from constructor import models
from drf_multiple_model.views import FlatMultipleModelAPIView
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.db.models.functions import Lower
from rest_framework.exceptions import APIException
from rest_framework import status
from haystack.query import SearchQuerySet, AutoQuery, Raw
import django_filters
from rest_framework import generics
from api.filters import CustomSearchFilter
from constructor.paginator import ResultsSetPagination
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
from api.filters import CustomSearchFilter


def elastic_search_specialization_results(query):
    results = []
    sqs = SearchQuerySet().models(models.Specialization)
    sqs = sqs.filter(name__search=query).order_by('id')[:30]
    for query in sqs:
        results.append({'id': query.object.id, 'name': query.object.name})
    return results


def elastic_search_institutes_results(query):
    results = []
    # sqs = SearchQuerySet().models(models.Institute)
    sqs = SearchQuerySet().models(models.InstituteCampus)
    sqs = sqs.filter(institute_name=query)
    query_list = sqs[:30]
    for query in query_list:
        results.append(
            {'id': query.object.institute.id,
             'name': query.object.institute.institute_name + ' (' + query.object.campus + ')'})
    return results


class SpecializationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Specialization
        fields = ['id', 'name']


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name']


class DisciplineNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ['id', 'name']


class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 25


class TextSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=500)


# class CourseSuggestion(APIView):
#     """
#     List all matches ,with in course, discipline,specialization. models
#     """
#
#     def get(self, request, format=None):
#         qs = models.Course.objects.all()
#         query_dict = {}
#         if request.GET.get('name'):
#             query_dict['name__contains'] = request.GET.get('name').strip()
#         qs = qs.filter(**query_dict).order_by('name')
#         serializer = CourseSuggestionSerializer(qs, many=True)
#         return Response(serializer.data)

def specialization_filter(queryset, request, *args, **kwargs):
    params = request.query_params['search']
    return queryset.filter(name__istartswith=params).annotate(name_lower=Lower("name")).distinct('name_lower').order_by(
        'name_lower')


class SpecializationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Specialization
        # fields = ('name',)
        fields = {
            'name': ['iexact'],
        }


class SpecializationList(generics.ListAPIView):
    queryset = models.Specialization.objects.all()
    serializer_class = TextSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']
    ordering = ['name']


class TextAPIView(APIView):

    def get(self, request):
        data = {'param': request.GET.get('search').strip(), 'results': []}
        if request.GET.get('search'):
            query = request.GET.get('search').strip()
            stop_words = set(stopwords.words('english'))
            query = re.sub(r'[?|$|.|!]', r'', query)
            word_tokens = word_tokenize(query)
            filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
            query = ' '.join(filtered_sentence)
            searchFilter = CustomSearchFilter()
            qs = searchFilter.filter_queryset(request=query, queryset=models.Specialization.objects.all(),
                                              view=['name'])
            qs = qs.order_by('id')
            paginator = ResultsSetPagination()

            page = paginator.paginate_queryset(qs, request)
            if page is not None:
                serializer = TextSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = TextSerializer(results, many=True)
            return Response(serializer.data)

            # for r in qs:
            #     data['results'].append({'id': r.id, 'name': r.name})

            # data['results'] = elastic_search_specialization_results(name)
            # print(qs, 'kkkk')
            # from django.db.models import Q
            # # qs = models.Specialization.objects.filter(name__istartswith=name).order_by('name')
            # qs = models.Specialization.objects.filter(name__istartswith=name).select_related().order_by('name')
            # if qs.count() == 0:
            #     qs = models.Specialization.objects.filter(name__icontains=name).order_by('name')
            # # ds = models.Discipline.objects.filter(name__icontains=name)
            # # results = chain(sp, ds)
            # # qs = sorted(results, key=lambda instance: instance.name, reverse=True)
            # qs = qs[:10]
            # print(qs)
            # for r in qs:
            #     data['results'].append({'id': r.id, 'name': r.name})
        # serializer = TextSerializer(qs, many=True)
        # return Response(serializer.data)
        return Response(data)


# class SpecializationDisciplineSuggestionView(FlatMultipleModelAPIView):
#     search_fields = ['name']
#     filter_backends = (filters.SearchFilter,)
#     pagination_class = LimitPagination
#     querylist = [
#
#         {'queryset': models.Discipline.objects.all(),
#          'serializer_class': DisciplineNameSerializer},
#         {'queryset': models.Specialization.objects.all(),
#          'serializer_class': SpecializationNameSerializer},
#     ]

# class SpecializationDisciplineSuggestionView(APIView):
#
#     def get(self, request, *args, **kwargs):
#         from django.db.models import Q, ExpressionWrapper, BooleanField
#         search_query = request.GET.get('search', '').strip()
#         if not search_query:
#             raise CustomApiException("Please provide atleast one character to search Institute by name",
#                                      status.HTTP_400_BAD_REQUEST)
#         query = models.Specialization.objects.filter(name__istartswith=search_query)[1:15]
#         results = []
#         for obj in query:
#             results.append({'id': obj.id, 'name': obj.name, 'type': 'Specialization'})
#
#         dump = json.dumps(results)
#         return HttpResponse(dump, content_type='application/json')


class SpecializationDisciplineSuggestionView(FlatMultipleModelAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitPagination
    querylist = [
        {'queryset': models.Specialization.objects.all().distinct('name'),
         'serializer_class': SpecializationNameSerializer,
         'filter_fn': specialization_filter},
    ]


# class UserProfileView(APIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = UserSerializer
#
#     def get_object(self):
#         return CustomUser.objects.get(id=self.request.user.id)


# def get(self, request, *args, **kwargs):
#     querylist = []
#     if request.GET.get('name'):
#
#         name = request.GET.get('name').strip()
#
#         querylist = [
#             {'queryset': models.Course.objects.filter(name__contains=name),
#              'serializer_class': CourseNameSerializer},
#             # {'queryset': models.Discipline.objects.filter(name__contains=name), 'serializer_class': CourseNameSerializer},
#         ]
#         print(querylist)
#     return Response({'results': json.dumps(querylist)})

class RegionNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ['id', 'name']


class CountryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ['id', 'name']


class InstituteGroupNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteGroup
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.display_name


class StateNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.name + ' (' + obj.country.name + ')'


class CityNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.City
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.name + ' (' + obj.state.country.name + ')'


# def country_filter(queryset, request, *args, **kwargs):
#     params = request.query_params['name']
#     return queryset.filter(name__startswith=params)

def country_filter(queryset, request, *args, **kwargs):
    if request.query_params.get('search'):
        params = request.query_params['search'].strip()
    else:
        params = request.query_params['name'].strip()
    if params:
        params = params.strip()
    return queryset.filter(name__istartswith=params)


def state_filter(queryset, request, *args, **kwargs):
    params = request.query_params['search'].strip()
    if params:
        params = params.strip()
    return queryset.filter(name__istartswith=params).order_by('name')


def city_filter(queryset, request, *args, **kwargs):
    params = request.query_params['search'].strip()
    if params:
        params = params.strip()
    return queryset.filter(name__istartswith=params).order_by('name')


class LocationAPIView(FlatMultipleModelAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitPagination
    querylist = [
        # {'queryset': models.Region.objects.all(),
        #  'serializer_class': RegionNameSerializer},
        {'queryset': models.Country.objects.all(),
         'serializer_class': CountryNameSerializer,
         'filter_fn': country_filter},
        {'queryset': models.State.objects.all(),
         'serializer_class': StateNameSerializer,
         'filter_fn': state_filter,
         },
        {'queryset': models.City.objects.all(),
         'serializer_class': CityNameSerializer,
         'filter_fn': city_filter,
         },

    ]

    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        results = self.get_empty_results()

        for query_data in querylist:
            self.check_query_data(query_data)

            queryset = self.load_queryset(query_data, request, *args, **kwargs)

            # Run the paired serializer
            context = self.get_serializer_context()
            data = query_data['serializer_class'](queryset, many=True, context=context).data

            label = self.get_label(queryset, query_data)

            # Add the serializer data to the running results tally
            results = self.add_to_results(data, label, results)

        formatted_results = self.format_results(results, request)

        if self.is_paginated:
            try:
                formatted_results = self.paginator.format_response(formatted_results)
            except AttributeError:
                raise NotImplementedError(
                    "{} cannot use the regular Rest Framework or Django paginators as is. "
                    "Use one of the included paginators from `drf_multiple_models.pagination "
                    "or subclass a paginator to add the `format_response` method."
                    "".format(self.__class__.__name__)
                )
        formatted_results.update({'param': request.GET.get('search')})
        formatted_results.move_to_end('param', last=False)
        return Response(formatted_results)


class InstituteNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Institute
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.institute_name + ' (' + obj.institutecampus_set.first().city.state.country.name + ')'


class InstituteCampusNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    campus_id = serializers.SerializerMethodField()
    institute_id = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteCampus
        fields = ['name', 'campus_id', 'institute_id']

    def get_name(self, obj):
        return obj.institute.institute_name + ' (' + obj.campus + ', ' + obj.city.name + ' )'

    def get_campus_id(self, obj):
        return obj.id

    def get_institute_id(self, obj):
        return obj.institute.id


class CourseTitleNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.CourseTitle
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.display_name


class BlogNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Blog
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.heading


class ScholarshipNameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Scholarship
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.scholarship_name


def institute_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(institute_name__istartswith=params)


def institute_campus_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    # return queryset.filter(campus__istartswith=params)
    return models.InstituteCampus.objects.filter(institute__institute_name__istartswith=params)
    # return queryset.filter(campus__isntitute__institute_name__istartswith=params)


def institute_group_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return models.InstituteGroup.objects.filter(display_name__istartswith=params)


def title_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(display_name__istartswith=params)


def course_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(name__istartswith=params)


def discipline_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(name__istartswith=params)


def specialization_site_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(name__istartswith=params)


def scholarship_site_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(scholarship_name__istartswith=params)


def blog_filter(queryset, request, *args, **kwargs):
    params = request.query_params['name']
    return queryset.filter(heading__istartswith=params)


class GenaricSuggestionAPIView(FlatMultipleModelAPIView):
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitPagination
    querylist = [
        {'queryset': models.InstituteGroup.objects.all(),
         'serializer_class': InstituteGroupNameSerializer,
         'filter_fn': institute_group_filter},
        {'queryset': models.Country.objects.all(),
         'serializer_class': CountryNameSerializer,
         'filter_fn': country_filter},
        {'queryset': models.Institute.objects.all(),
         'serializer_class': InstituteNameSerializer,
         'filter_fn': institute_filter},
        # {'queryset': models.InstituteCampus.objects.all(),
        #  'serializer_class': InstituteCampusNameSerializer,
        #  'filter_fn': institute_campus_filter},
        {'queryset': models.Course.objects.all(),
         'serializer_class': CourseNameSerializer,
         'filter_fn': course_filter},
        {'queryset': models.Discipline.objects.all(),
         'serializer_class': DisciplineNameSerializer,
         'filter_fn': discipline_filter},
        {'queryset': models.Scholarship.objects.all(),
         'serializer_class': ScholarshipNameSerializer,
         'filter_fn': scholarship_site_filter},
        {'queryset': models.Blog.objects.all(),
         'serializer_class': BlogNameSerializer,
         'filter_fn': blog_filter},

    ]


class AllSearchSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_name(self, obj):
        if str(obj._meta.model.__name__) == "CourseTitle":
            return obj.display_name
        else:
            return obj.name

    def get_type(self, obj):
        return obj._meta.model.__name__


class AllSearch(APIView):

    def get(self, request, *args, **kwargs):
        from django.db.models import Q, ExpressionWrapper, BooleanField
        search_query = request.GET.get('q', '').strip()
        if not search_query:
            raise APIException("Please provide atleast one character to search Institute by name",
                               status.HTTP_400_BAD_REQUEST)

        course_title_results = models.CourseTitle.objects.filter(
            Q(display_name__istartswith=search_query) | Q(display_name__icontains=search_query)
        ).annotate(
            is_start=ExpressionWrapper(
                Q(display_name__istartswith=search_query),
                output_field=BooleanField()
            )
        ).order_by('-is_start')
        course_results = models.Course.objects.filter(
            Q(name__istartswith=search_query) | Q(name__icontains=search_query)
        ).annotate(
            is_start=ExpressionWrapper(
                Q(name__istartswith=search_query),
                output_field=BooleanField()
            )
        ).order_by('-is_start')
        discipline_results = models.Discipline.objects.filter(
            Q(name__istartswith=search_query) | Q(name__icontains=search_query)
        ).annotate(
            is_start=ExpressionWrapper(
                Q(name__istartswith=search_query),
                output_field=BooleanField()
            )
        ).order_by('-is_start')
        specialization_results = models.Specialization.objects.filter(
            Q(name__istartswith=search_query) | Q(name__icontains=search_query)
        ).annotate(
            is_start=ExpressionWrapper(
                Q(name__istartswith=search_query),
                output_field=BooleanField()
            )
        ).order_by('-is_start')

        # combine querysets
        queryset_chain = chain(
            course_title_results,
            course_results,
            discipline_results,
            specialization_results,

        )
        qs = sorted(queryset_chain,
                    key=lambda
                        instance: instance.display_name if str(
                        instance._meta.model.__name__) == "CourseTitle" else instance.name,
                    reverse=True)
        relevant = []
        irr_relevant = []

        for idx in qs:
            if str(idx._meta.model.__name__) == "CourseTitle":
                if idx.display_name.lower().startswith(search_query):
                    relevant.append(idx)
                else:
                    irr_relevant.append(idx)
            else:
                if idx.name.lower().startswith(search_query):
                    relevant.append(idx)
                else:
                    irr_relevant.append(idx)

        results = relevant + irr_relevant

        # res = [idx for idx in qs if idx.name.lower().startswith(search_query)]
        # print(res)

        serializer = AllSearchSerializer(results, many=True)
        return Response(serializer.data)


class InstitutesSearch(APIView):
    serializer = InstituteNameSerializer

    def get(self, request, *args, **kwargs):
        # from django.db.models import Q, ExpressionWrapper, BooleanField
        results = []
        searchFilter = CustomSearchFilter()
        # qs = models.InstituteCampus.objects.all()
        qs = models.Institute.objects.all()
        search_query = request.GET.get('q', '')
        stopwords = ['uni', 'univ', 'unive', 'univer', 'univers', 'universi', 'universit', 'university',
                     'of']
        search_query = search_query.split()
        resultwords = [word for word in search_query if word.lower() not in stopwords]
        search_query = ' '.join(resultwords)
        if search_query:
            query_list = searchFilter.filter_queryset(request=search_query, queryset=qs,
                                                      view=['institute_name', ])
            serializer = self.serializer(query_list,many=True)
            return Response(serializer.data)
            # for query in query_list:
            #     results.append(
            #         {'id': query.institute.id,
            #          'campus_id': query.id,
            #          'name': query.institute.institute_name + ' (' + query.campus + ',' + query.city.name + ')', })
            # results = {'param': search_query, 'results': results}
        # result['results'] = elastic_search_institutes_results(search_query)
        return Response(results)
        # if not search_query:
        #     raise APIException("Please provide atleast one character to search Institute by name",
        #                        status.HTTP_400_BAD_REQUEST)
        # qs = models.Institute.objects.filter(
        #     Q(institute_name__istartswith=search_query) | Q(institute_name__icontains=search_query)
        # ).annotate(
        #     is_start=ExpressionWrapper(
        #         Q(institute_name__istartswith=search_query)
        #         | Q(institute_name__icontains=search_query),
        #         output_field=BooleanField()
        #     )
        # ).order_by('-is_start')
        #
        # serializer = InstituteNameSerializer(qs, many=True)
        # return Response(serializer.data)
