from django.db.models import Q
from constructor import models as myModels
import re
from .helper import get_distance
from api.filters import CustomSearchFilter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re
from itertools import chain
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def get_coures_query(name):
    if name:
        name = name.strip()
        return myModels.Course.objects.filter(Q(name__search=name)
                                              | Q(specialization__name__istartswith=name)
                                              | Q(discipline__name__istartswith=name)
                                              | Q(course_title__display_name__istartswith=name)
                                              )
    else:
        return myModels.Course.objects.all()


from rest_framework.filters import SearchFilter


def get_search_terms(params):
    """
    Search terms are set by a ?search=... query parameter,
    and may be comma and/or whitespace delimited.
    """
    params = params.replace('\x00', '')  # strip null characters
    params = params.replace(',', ' ')
    return params.split()


def get_filtered_courses(request):
    searchFilter = CustomSearchFilter()
    all_query_set = myModels.Course.objects.all()
    qs = myModels.Course.objects.filter(name__isnull=True)
    if request.data.get("course"):
        keywords = request.data.get("course")
        if isinstance(keywords, str):
            stop_words = set(stopwords.words('english'))
            query = re.sub(r'[?|$|.|!&]', r'', keywords)
            word_tokens = word_tokenize(query)
            filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
            query = ' '.join(filtered_sentence)
            keywords = query
        # query = Q()
        for keyword in keywords:
            #  updated
            # stop_words = set(stopwords.words('english'))
            query = re.sub(r'[?|$|.|!&]', r'', keyword)
            # word_tokens = word_tokenize(query)
            # filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
            # query = ' '.join(filtered_sentence)
            keyword = query
            qs_filter = searchFilter.filter_queryset(request=keyword, queryset=all_query_set,
                                                     view=['name', 'specialization__name'])
            qs = qs | qs_filter

            #  previous
            # query.add(Q(name__search=keyword), Q.OR)
            # query.add(Q(specialization__name__search=keyword), Q.OR)
            # query.add(Q(course_title__display_name__search=keyword), Q.OR)
        # qs = qs.order_by('name').distinct('name')
    else:
        qs = myModels.Course.objects.all()

    query_dict = {}
    if request.data.get("google_location"):
        google_location = request.data.get("google_location")
        distance = google_location.get("distance")
        latitude = google_location.get("latitude")
        longitude = google_location.get("longitude")
        d = get_distance(latitude, longitude)
        camp_qs = myModels.InstituteCampus.objects.annotate(distance=d).order_by('distance').filter(
            distance__lt=distance)
        campus_list = list(camp_qs.filter().values_list('id'))
        qs = qs.filter(campus__in=campus_list)
    query = Q()
    if request.data.get("regions"):
        query_dict['campus__city__state__country__region__in'] = request.data.get("regions")
    if request.data.get("countries"):
        query.add(Q(campus__city__state__country__in=request.data.get("countries")), Q.OR)
        # query_dict['campus__city__state__country__in'] = request.data.get("countries")
    if request.data.get("states"):
        query.add(Q(campus__city__state__in=request.data.get("states")), Q.OR)
        # query_dict['campus__city__state__in'] = request.data.get("states")
    if request.data.get("cities"):
        query.add(Q(campus__city__in=request.data.get("cities")), Q.OR)
        # query_dict['campus__city__in'] = request.data.get("cities")
    qs = qs.filter(query)
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
    # if request.data.get("fees"):
    #     query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
    if request.data.get("institutes"):
        query_dict['campus__institute__in'] = request.data.get("institutes")
    if request.data.get("campuses"):
        query_dict['campus__in'] = request.data.get("campuses")
    if request.data.get("panels"):
        query_dict['campus__institute__institute_panel__in'] = request.data.get("panels")
    if request.data.get("institute_groups"):
        query_dict['campus__institute__institute_group__in'] = request.data.get("institute_groups")
    if request.data.get("pathway_groups"):
        query_dict['campus__institute__pathway_group__in'] = request.data.get("pathway_groups")
    if request.data.get("apply_portals"):
        query_dict['campus__institute__apply_portal__in'] = request.data.get("apply_portals")

    if query_dict:
        qs = qs.filter(**query_dict)

    if request.data.get("fees"):
        fees = request.data.get("fees")
        if fees[1] < 5000000:
            qs = qs.filter(base_fee__range=fees)
        else:
            qs = qs.filter(base_fee__gte=fees[0])

    if request.data.get("durations"):
        durations = request.data.get("durations")
        if durations[1] < 5:
            qs = qs.filter(
                Q(courseduration__duration_one__range=durations) |
                Q(courseduration__duration_two__range=durations) |
                Q(courseduration__duration_three__range=durations))
        else:
            qs = qs.filter(
                Q(courseduration__duration_one__gte=durations[0]) |
                Q(courseduration__duration_two__gte=durations[0]) |
                Q(courseduration__duration_three__gte=durations[0]))

    if request.data.get("order"):
        order = request.data.get("order")
        if order == 0:
            qs = qs.order_by('name')
        if order == 1:
            tbc = qs.filter(Q(base_fee=0) | Q(base_fee__isnull=True))
            qs = qs.filter(base_fee__gt=0)
            qs = qs.order_by('base_fee')
            # qs = qs | tbc
            qs = list(chain(qs, tbc))
        if order == 2:
            tbc = qs.filter(Q(base_fee=0) | Q(base_fee__isnull=True))
            qs = qs.filter(base_fee__gt=0)
            qs = qs.order_by('-base_fee')
            qs = list(chain(qs, tbc))
        if order == 3:
            qs = qs.order_by('courseduration__duration_one')
        if order == 4:
            qs = qs.order_by('-courseduration__duration_one')
        if order == 5:
            qs = qs.order_by('campus__institute__institute_panel')

    else:
        qs = qs.order_by('name')
    return qs


def get_course_title(keywords):
    for keyword in keywords:
        course_title_qs = myModels.CourseTitle.objects.filter(key=keyword).first()
        if course_title_qs:
            return course_title_qs
    return None


def get_search_courses(request):
    # stop_words = set(stopwords.words('english'))
    stop_words = set(myModels.StopQueryWord.objects.all().values_list('stop_word', flat=True))
    keywords = request.data.get("course")
    searchFilter = CustomSearchFilter()
    all_courses = myModels.Course.objects.all()
    qs = myModels.Course.objects.filter(name__isnull=True)
    if keywords:
        if isinstance(keywords, str):
            # stop_words = set(stopwords.words('english'))
            query = re.sub(r'[?|$|.|!&]', r'', keywords)
            word_tokens = word_tokenize(query)
            filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
            query = ' '.join(filtered_sentence)
            qs = searchFilter.filter_queryset(request=query, queryset=all_courses,
                                              view=['name', 'specialization__name', 'course_title__key'])
        else:
            keywords = [x.lower() for x in keywords]
            for keyword in keywords:
                keyword = re.sub(r'[?|$|.|!&]', r'', keyword)
                word_tokens = word_tokenize(keyword)
                filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
                query = ' '.join(filtered_sentence)
                keyword = query
                qs_filter = searchFilter.filter_queryset(request=keyword, queryset=all_courses,
                                                         view=['name', 'specialization__name', 'course_title__key'])
                qs = qs | qs_filter

            #      new  for course title
            course_title_instance = get_course_title(keywords)
            if course_title_instance:
                query_dict = {'course_title__key': course_title_instance.key}
                qs = qs.filter(**query_dict)
            #      new  for course title

    else:
        qs = all_courses
    return qs


def apply_filter_on_courses(request, qs):
    query_dict = {}
    if request.data.get("google_location"):
        google_location = request.data.get("google_location")
        distance = google_location.get("distance")
        latitude = google_location.get("latitude")
        longitude = google_location.get("longitude")
        d = get_distance(latitude, longitude)
        camp_qs = myModels.InstituteCampus.objects.annotate(distance=d).order_by('distance').filter(
            distance__lt=distance)
        campus_list = list(camp_qs.filter().values_list('id'))
        qs = qs.filter(campus__in=campus_list)
    query = Q()
    if request.data.get("regions"):
        query_dict['campus__city__state__country__region__in'] = request.data.get("regions")
    if request.data.get("countries"):
        query.add(Q(campus__city__state__country__in=request.data.get("countries")), Q.OR)
        # query_dict['campus__city__state__country__in'] = request.data.get("countries")
    if request.data.get("states"):
        query.add(Q(campus__city__state__in=request.data.get("states")), Q.OR)
        # query_dict['campus__city__state__in'] = request.data.get("states")
    if request.data.get("cities"):
        query.add(Q(campus__city__in=request.data.get("cities")), Q.OR)
        # query_dict['campus__city__in'] = request.data.get("cities")
    qs = qs.filter(query)
    if request.data.get("degree_levels"):
        query_dict['degree_level__in'] = request.data.get("degree_levels")
    else:
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
    # if request.data.get("fees"):
    #     query_dict['coursefee__ceil_value__range'] = request.data.get("fees")
    if request.data.get("institutes"):
        query_dict['campus__institute__in'] = request.data.get("institutes")
    if request.data.get("campuses"):
        query_dict['campus__in'] = request.data.get("campuses")
    if request.data.get("panels"):
        query_dict['campus__institute__institute_panel__in'] = request.data.get("panels")
    if request.data.get("institute_groups"):
        query_dict['campus__institute__institute_group__in'] = request.data.get("institute_groups")
    if request.data.get("pathway_groups"):
        query_dict['campus__institute__pathway_group__in'] = request.data.get("pathway_groups")
    if request.data.get("apply_portals"):
        query_dict['campus__institute__apply_portal__in'] = request.data.get("apply_portals")

    if query_dict:
        qs = qs.filter(**query_dict)

    if request.data.get("fees"):
        fees = request.data.get("fees")
        if fees[1] < 5000000:
            qs = qs.filter(base_fee__range=fees)
        elif fees[0] > 0:
            qs = qs.filter(base_fee__gte=fees[0])

    if request.data.get("durations"):
        durations = request.data.get("durations")
        if durations[1] < 5:
            qs = qs.filter(
                Q(courseduration__duration_one__range=durations) |
                Q(courseduration__duration_two__range=durations) |
                Q(courseduration__duration_three__range=durations))
        else:
            qs = qs.filter(
                Q(courseduration__duration_one__gte=durations[0]) |
                Q(courseduration__duration_two__gte=durations[0]) |
                Q(courseduration__duration_three__gte=durations[0]))

    if request.data.get("order"):
        order = request.data.get("order")
        if order == 0:
            qs = qs.order_by('name')
        if order == 1:
            # tbc = qs.filter(Q(base_fee=0) | Q(base_fee__isnull=True))
            tbc = qs.filter(base_fee__isnull=True)
            tbc_zero = qs.filter(base_fee=0)
            # qs = qs.filter(base_fee__gt=0)
            qs = qs.filter(base_fee__gt=0)
            qs = qs.order_by('base_fee')
            # qs = qs | tbc
            qs = list(chain(tbc_zero, qs, tbc))
        if order == 2:
            # tbc = qs.filter(Q(base_fee=0) | Q(base_fee__isnull=True))
            tbc = qs.filter(base_fee__isnull=True)
            tbc_zero = qs.filter(base_fee=0)
            qs = qs.filter(base_fee__gt=0)
            qs = qs.order_by('-base_fee')
            qs = list(chain(qs, tbc_zero, tbc))
            # qs = qs | tbc
        if order == 3:
            qs = qs.order_by('courseduration__duration_one')
        if order == 4:
            qs = qs.order_by('-courseduration__duration_one')
        if order == 5:
            qs = qs.order_by('campus__institute__institute_panel')

    else:
        qs = qs.order_by('name')
    return qs


def courses_group_by_institutes(course_query):
    results = []
    institutes = list(set(course_query.values_list('campus__institute', flat=True)))
    institutes = myModels.Institute.objects.filter(id__in=institutes)

    for course in course_query:
        for institute in institutes:
            if institute.id == course.campus.institute.id:
                status = True
                for result in results:
                    if result['institute'].id == course.campus.institute.id:
                        result['courses'].append(course)
                        status = False
                        break
                if status:
                    results.append({'institute': institute, 'courses': [course]})

    return results


def get_filtered_scholarships(request):
    scholarships = myModels.Scholarship.objects.all()

    query = Q()
    if request.data.get("countries"):
        query.add(Q(institute__institutecampus__city__state__country__in=request.data.get("countries")), Q.OR)
        query.add(Q(institute_name_organizational_scholarship__country__in=request.data.get("countries")), Q.OR)

    qs = scholarships.filter(query)
    query_dict = {}
    if request.data.get('scholarship'):
        query_dict['scholarship_name__search'] = request.data.get('scholarship').strip()
    if request.data.get("types"):
        query_dict['scholarship_type__in'] = request.data.get("types")
    if request.data.get("degree_levels"):
        query_dict['degree_level__in'] = request.data.get("degree_levels")
    if request.data.get("degree_level_types"):
        query_dict['degree_level__level_type__in'] = request.data.get("degree_level_types")
    if request.data.get("disciplines"):
        query_dict['discipline__in'] = request.data.get("disciplines")
    if request.data.get("deadline_months"):
        query_dict['scholarshipclosedate__month__in'] = request.data.get("deadline_months")
    if request.data.get("years"):
        query_dict['scholarshipclosedate__year__in'] = request.data.get("years")
    if request.data.get("institutes"):
        query_dict['institute__in'] = request.data.get("institutes")
    if request.data.get("institute_groups"):
        query_dict['institute__institute_group__in'] = request.data.get("institute_groups")
    if request.data.get("pathway_groups"):
        query_dict['institute__pathway_group__in'] = request.data.get("pathway_groups")

    if query_dict:
        qs = qs.filter(**query_dict)

    if request.data.get("order"):
        order = request.data.get("order")
        if order == 1:
            qs = qs.order_by('scholarship_name')
        if order == 2:
            qs = qs.order_by('-scholarship_name')
        if order == 3:
            qs = qs.order_by('scholarshipclosedate__month')
    else:
        qs = qs.order_by('scholarship_name')

    return qs.distinct()
