from django.db.models import Count
from rest_framework import serializers

from api.serializers.scholarship import ScholarshipTypeCountSerializer
from constructor import models
from api.serializers import institute, discipline as disciplines_serializer, degree_level as degree_level_serializer
from api.helper import get_ranking
from constructor.helper import headers


class CrmCourseDetailsSerializer(serializers.ModelSerializer):
    course_id = serializers.SerializerMethodField()
    campus_name = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    discipline_name = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    campus_address = serializers.SerializerMethodField()
    course_language = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    degree_level = serializers.SerializerMethodField()
    institute_sector = serializers.SerializerMethodField()
    program_discipline = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'course_id', 'campus_name', 'country_name',
                  'discipline_name', 'institute_name',
                  'campus_address', 'course_language',
                  'course_title', 'degree_level', 'institute_sector',
                  'program_discipline', 'specialization',
                  ]

    def get_course_id(self, obj):
        return obj.id

    def get_campus_name(self, obj):
        return obj.campus.campus

    def get_country_name(self, obj):
        return obj.campus.city.state.country.name

    def get_discipline_name(self, obj):
        return obj.discipline.name

    def get_institute_name(self, obj):
        return obj.campus.institute.institute_name

    def get_campus_address(self, obj):
        return obj.campus.campus + ',' + obj.campus.city.state.name + ',' + obj.campus.city.state.country.name

    def get_course_language(self, obj):
        return obj.course_language

    def get_course_title(self, obj):
        return obj.course_title.display_name

    def get_degree_level(self, obj):
        return obj.degree_level.display_name

    def get_institute_sector(self, obj):
        return obj.campus.institute.sector

    def get_program_discipline(self, obj):
        return obj.discipline.name

    def get_specialization(self, obj):
        return obj.specialization.name


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name', ]


class AllCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name']


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name', 'discipline', 'campus']


class CourseDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseDuration
        fields = ['id', 'type', 'duration_one', 'duration_two', 'duration_three']


class CourseIntakeAndDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseIntakeAndDeadLine
        fields = ['id', 'intake_month', 'intake_day', 'intake_year', 'deadline_day', 'deadline_months', 'deadline_year',
                  'application_open_day', 'application_open_months', 'application_open_year', 'rolling_intake',
                  'rolling_deadline']


class CurrencyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ['id', 'display_name', 'value_to_pkr']


class FeeDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyDetailSerializer()

    class Meta:
        model = models.CourseFee
        fields = ['id', 'type', 'currency', 'ceil_value', 'floor_value']


class CourseApplyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseApply
        fields = ['id', 'type', 'url']


class CourseExamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseExam
        fields = ['id', 'exam_type', 'required', 'score']


class CourseDetailsSerializer(serializers.ModelSerializer):
    campus = institute.CampusDetailSerializer()
    discipline = disciplines_serializer.DisciplineDetailViewSerializer()
    specialization = disciplines_serializer.SpecializationDetailViewSerializer()
    course_title = disciplines_serializer.CourseTitleDetailViewSerializer()
    degree_level = degree_level_serializer.DegreeLevelViewSerializer()
    course_duration = CourseDurationSerializer(source='courseduration_set', many=True)
    admission_schedule = CourseIntakeAndDeadLineSerializer(source='courseintakeanddeadline_set', many=True)
    fee = FeeDetailSerializer(source='coursefee_set', many=True)
    exams = CourseExamDetailSerializer(source='courseexam_set', many=True)
    source_links = CourseApplyDetailSerializer(source='courseapply_set', many=True)
    ranking = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = [field.name for field in models.Course._meta.fields] + ['course_duration', 'admission_schedule', 'fee',
                                                                         'exams', 'source_links', 'ranking']

    def get_ranking(self, obj):
        data = {
            'qs_world_ranking': get_ranking(headers.QAS_WORLD_RANKING, obj.campus.institute),
            'times_higher_world_ranking': get_ranking(headers.TIMES_HIGHER_WORLD_RANKING, obj.campus.institute),
            'us_news_world_ranking': get_ranking(headers.US_NEWS_WORLD_RANKING, obj.campus.institute),
            'us_news_national_ranking': get_ranking(headers.US_NEWS_NATIONAL_RANKING, obj.campus.institute),
            'shanghai_ranking': get_ranking(headers.SHANGHAI_RANKING, obj.campus.institute),
            'tcf_ranking': get_ranking(headers.TCF_RANKING, obj.campus.institute),
        }
        return data


class InstituteNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Institute
        fields = ['id', 'institute_name', 'logo', 'sector', 'institute_type']


class CourseCardSerializer(serializers.ModelSerializer):
    discipline = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()
    degree_level = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    campus = serializers.SerializerMethodField()
    course_duration = serializers.SerializerMethodField()
    course_fee = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'base_fee', 'course_language',
                  'discipline', 'specialization', 'degree_level', 'course_title', 'campus',
                  'course_duration', 'course_fee', 'country', 'institute',
                  ]

    def get_discipline(self, obj):
        return obj.discipline.name

    def get_institute(self, obj):
        serializer = InstituteNameSerializer(obj.campus.institute)
        return serializer.data

    def get_specialization(self, obj):
        return obj.specialization.name

    def get_degree_level(self, obj):
        return obj.degree_level.display_name

    def get_course_title(self, obj):
        return obj.course_title.display_name

    def get_country(self, obj):
        return obj.campus.city.state.country.name

    def get_campus(self, obj):
        camp = {
            "name": obj.campus.campus + ',' + obj.campus.city.state.name + ',' + obj.campus.city.state.country.name,
            "latitude": obj.campus.latitude,
            "longitude": obj.campus.longitude,
            "id": obj.campus.id
        }
        return camp

    def get_course_duration(self, obj):
        years = obj.courseduration_set.filter(type='year')
        year_string = ''
        for year in years:
            year_string = year_string + str(year.duration_one)
            if year.duration_two:
                year_string = year_string + ',' + str(year.duration_two)
            if year.duration_three:
                year_string = year_string + ',' + str(year.duration_three)

        if year_string:
            return year_string + ' Years'

        semesters = obj.courseduration_set.filter(type='semester')
        semester_string = ''
        for semester in semesters:
            semester_string = semester_string + str(semester.duration_one)
            if semester.duration_two:
                semester_string = semester_string + ',' + str(semester.duration_two)
            if semester.duration_three:
                semester_string = semester_string + ',' + str(semester.duration_three)

        if semester_string:
            return semester_string + 'Semesters'

    def get_course_fee(self, obj):
        fees = obj.coursefee_set.filter(type='fee_per_year')
        fee_per_year_string = ''
        for fee in fees:
            fee_per_year_string = fee_per_year_string + str(fee.ceil_value) + ' ' + fee.currency.display_name

        # return fee_per_year_string
        serializer = FeeDetailSerializer(fees, many=True)
        return serializer.data


class CourseCardGroupSerializer(serializers.ModelSerializer):
    discipline = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()
    degree_level = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    campus = serializers.SerializerMethodField()
    course_duration = serializers.SerializerMethodField()
    course_fee = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()
    related_course = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'base_fee', 'course_language',
                  'discipline', 'specialization', 'degree_level', 'course_title', 'campus',
                  'course_duration', 'course_fee', 'country', 'institute',
                  'related_course', ]

    def get_related_course(self, obj):
        qs = self.context.get('courses')
        # results = qs.filter(campus__institute=obj.campus.institute).exclude(id__in=[obj.id]).values_list('id', flat=True)
        results = qs.filter(campus=obj.campus).exclude(id__in=[obj.id]).values_list('id', flat=True)
        # results = []
        # for obj in qs:
        #     results.append({'id': obj.id, 'name': obj.name,
        #                     # 'specialization':obj.specialization.name,
        #                     })
        return results

    def get_discipline(self, obj):
        return obj.discipline.name

    def get_institute(self, obj):
        serializer = InstituteNameSerializer(obj.campus.institute)
        return serializer.data

    def get_specialization(self, obj):
        return obj.specialization.name

    def get_degree_level(self, obj):
        return obj.degree_level.display_name

    def get_course_title(self, obj):
        return obj.course_title.display_name

    def get_country(self, obj):
        return obj.campus.city.state.country.name

    def get_campus(self, obj):
        camp = {
            "name": obj.campus.campus + ',' + obj.campus.city.state.name + ',' + obj.campus.city.state.country.name,
            "latitude": obj.campus.latitude,
            "longitude": obj.campus.longitude,
            "id": obj.campus.id
        }
        return camp

    def get_course_duration(self, obj):
        years = obj.courseduration_set.filter(type='year')
        year_string = ''
        for year in years:
            year_string = year_string + str(year.duration_one)
            if year.duration_two:
                year_string = year_string + ',' + str(year.duration_two)
            if year.duration_three:
                year_string = year_string + ',' + str(year.duration_three)

        if year_string:
            return year_string + ' Years'

        semesters = obj.courseduration_set.filter(type='semester')
        semester_string = ''
        for semester in semesters:
            semester_string = semester_string + str(semester.duration_one)
            if semester.duration_two:
                semester_string = semester_string + ',' + str(semester.duration_two)
            if semester.duration_three:
                semester_string = semester_string + ',' + str(semester.duration_three)

        if semester_string:
            return semester_string + 'Semesters'

    def get_course_fee(self, obj):
        fees = obj.coursefee_set.filter(type='fee_per_year')
        fee_per_year_string = ''
        for fee in fees:
            fee_per_year_string = fee_per_year_string + str(fee.ceil_value) + ' ' + fee.currency.display_name

        # return fee_per_year_string
        serializer = FeeDetailSerializer(fees, many=True)
        return serializer.data


class RelatedCourseCardSerializer(serializers.ModelSerializer):
    discipline = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()
    degree_level = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    campus = serializers.SerializerMethodField()
    course_duration = serializers.SerializerMethodField()
    course_fee = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'campus', 'name', 'discipline', 'specialization', 'degree_level', 'course_title',
                  'course_language', 'country',
                  'course_duration', 'course_fee', 'institute', 'base_fee']

    def get_discipline(self, obj):
        return obj.discipline.name

    def get_institute(self, obj):
        serializer = InstituteNameSerializer(obj.campus.institute)
        return serializer.data

    def get_specialization(self, obj):
        return obj.specialization.name

    def get_degree_level(self, obj):
        return obj.degree_level.display_name

    def get_course_title(self, obj):
        return obj.course_title.display_name

    def get_country(self, obj):
        return obj.campus.city.state.country.name

    def get_campus(self, obj):
        camp = {
            "name": obj.campus.campus + ',' + obj.campus.city.state.name + ',' + obj.campus.city.state.country.name,
            "id": obj.campus.id
        }
        return camp

    def get_course_duration(self, obj):
        years = obj.courseduration_set.filter(type='year')
        year_string = ''
        for year in years:
            year_string = year_string + str(year.duration_one)
            if year.duration_two:
                year_string = year_string + ',' + str(year.duration_two)
            if year.duration_three:
                year_string = year_string + ',' + str(year.duration_three)

        if year_string:
            return year_string + ' Years'

        semesters = obj.courseduration_set.filter(type='semester')
        semester_string = ''
        for semester in semesters:
            semester_string = semester_string + str(semester.duration_one)
            if semester.duration_two:
                semester_string = semester_string + ',' + str(semester.duration_two)
            if semester.duration_three:
                semester_string = semester_string + ',' + str(semester.duration_three)

        if semester_string:
            return semester_string + 'Semesters'

    def get_course_fee(self, obj):
        fees = obj.coursefee_set.filter(type='fee_per_year')
        fee_per_year_string = ''
        for fee in fees:
            fee_per_year_string = fee_per_year_string + str(fee.ceil_value) + ' ' + fee.currency.display_name

        # return fee_per_year_string
        serializer = FeeDetailSerializer(fees, many=True)
        return serializer.data


class CoursesGroupSerializer(serializers.Serializer):
    institute = InstituteNameSerializer()
    courses = CourseCardSerializer(many=True)


class CourseCompareSerializer(serializers.ModelSerializer):
    campus = institute.CampusDetailSerializer()
    # discipline = disciplines_serializer.DisciplineDetailViewSerializer()
    specialization = disciplines_serializer.SpecializationDetailViewSerializer()
    # course_title = disciplines_serializer.CourseTitleDetailViewSerializer()
    degree_level = degree_level_serializer.DegreeLevelViewSerializer()

    course_duration = CourseDurationSerializer(source='courseduration_set', many=True)
    intakes = CourseIntakeAndDeadLineSerializer(source='courseintakeanddeadline_set', many=True)
    fee = FeeDetailSerializer(source='coursefee_set', many=True)

    # exams = CourseExamDetailSerializer(source='courseexam_set', many=True)
    scholarship = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ["name", 'campus', 'degree_level', 'specialization', 'course_duration', 'fee', 'intakes',
                  'scholarship']

    def get_scholarship(self, obj):
        try:
            scholarships = models.Scholarship.objects.filter(degree_level=obj.degree_level, discipline=obj.discipline,
                                                             institute__institutecampus=obj.campus)
            scholarships_types = models.ScholarshipType.objects.filter(scholarship__in=scholarships).annotate(
                scholarship_count=Count('scholarship'))

            serializer = ScholarshipTypeCountSerializer(scholarships_types, many=True)

            return serializer.data
        except AttributeError:
            return []


class CourseAllLocationsCitiesSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ['id', 'name', 'course_count']

    def get_course_count(self, obj):
        return 0


class CourseAllLocationsStatesSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    cities = CourseAllLocationsCitiesSerializer(source="city_set", many=True)

    class Meta:
        model = models.State
        fields = ['id', 'name', 'course_count', 'cities']

    def get_course_count(self, obj):
        return 0


class CourseAllLocationsSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    states = CourseAllLocationsStatesSerializer(source="state_set", many=True)

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'course_count', 'states']

    def get_course_count(self, obj):
        return 0


class CourseRelatedInstitutesSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Country
        fields = ['id', 'name', 'course_count']

    def get_course_count(self, obj):
        return obj.course_count

    def get_name(self, obj):
        return obj.institute_name


class CourseRelatedCampusesSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.InstituteCampus
        fields = ['id', 'name', 'course_count']

    def get_course_count(self, obj):
        return obj.course_count

    def get_name(self, obj):
        return obj.campus
