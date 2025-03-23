import pandas as pd
from constructor.helper import headers
from constructor import models
from constructor import forms
from constructor.helper.schedule_helper import create_or_update_admission_schedule


def parse_header_error(errors):
    return [{'key': field,
             'error': ' Column does not exist in given file against  (columns are case '
                      'sensitive)'}
            for field in errors]


def parse_error(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


class CourseExcelToJsonParser:
    # def __init__(self, file):
    #     self.df = pd.read_excel(file)
    #     self.df.columns = self.df.columns.str.replace('\n', '')
    #     self.df.columns = self.df.columns.str.strip()
    #     self.df = self.df.fillna('None')
    #     self.header = self.df.columns.ravel()
    #     self.data = self.df.to_dict(orient='records')
    #     self.clean_data()

    def __init__(self, df):
        self.df = df
        self.df.columns = self.df.columns.str.replace('\n', '')
        self.df.columns = self.df.columns.str.strip()
        self.df = self.df.fillna('None')
        self.header = self.df.columns.ravel()
        self.data = self.df.to_dict(orient='records')
        self.clean_data()

    def clean_data(self):
        for data in self.data:
            for key in data:
                if data[key] == 'None':
                    data[key] = None
                # if data[key] == 'yes' or data[key] == 'Yes' or data[key] == 'YES':
                #     data[key] = 'yes'
                if isinstance(data[key], str):
                    data[key] = data[key].strip()
                    if len(data[key]) == 0:
                        data[key] = None
                if data.get(headers.INSTITUTE_TYPE):
                    data[headers.INSTITUTE_TYPE] = data.get(headers.INSTITUTE_TYPE).upper()
                if data.get(headers.INSTITUTE_SECTOR):
                    data[headers.INSTITUTE_SECTOR] = data.get(headers.INSTITUTE_SECTOR).upper()

    def get_header(self):
        default_header = set(headers.COMMON_HEADER)
        difference = default_header.difference(set(self.header))
        if difference:
            return False, parse_header_error(list(difference))
        return True, None

    def get_data(self):
        status, differance = self.get_header()
        if status:
            row = 2
            for data in self.data:
                institute_campus_status, institute_campus = create_or_get_institute_campus(data, row)
                if institute_campus_status:
                    response_status, response = get_discipline_degree_level_title_specialization(data, row)
                    if response_status:
                        course_status, course_response = create_or_update_course(data, institute_campus, response, row)
                        if not course_status:
                            return course_status, course_response
                    else:
                        return response_status, response
                else:
                    return institute_campus_status, institute_campus
                row = row + 1

            return status, None
        else:
            return status, differance


def get_or_create_complete_course(data, row):
    institute_status, institute = create_or_get_institute_campus(data, row)
    if institute_status:
        response_status, response = get_discipline_degree_level_title_specialization(data, row)
        if response_status:
            course_status, course_response = create_or_update_course(data, institute, response, row)
            if not course_status:
                return course_status, course_response
        else:
            return response_status, response
    else:
        return institute_status, institute
    return True, None


def get_or_create_country(data, row):
    country_form = forms.CountryForm(data)
    if country_form.is_valid():
        data = country_form.cleaned_data
        country = models.Country.objects.filter(name__iexact=data.get('name')).first()
        if not country:
            country = country_form.save()
        return True, country
    else:
        errors = parse_error(country_form.errors, row)
        return False, errors


def create_or_get_state(data, row):
    country_status, country_response = get_or_create_country(data, row)
    if country_status:
        state_form = forms.StateForm(data, initial={'country': country_response})
        if state_form.is_valid():
            data = state_form.cleaned_data
            state = models.State.objects.filter(name__iexact=data.get('name'), country=country_response).first()
            if not state:
                state = state_form.save()
            return True, state
        else:
            errors = parse_error(state_form.errors, row)
            return False, errors
    else:
        return country_status, country_response,


def create_or_get_city(data, row):
    state_status, state_response = create_or_get_state(data, row)
    if state_status:
        city_form = forms.CityForm(data, initial={'state': state_response})
        if city_form.is_valid():
            data = city_form.cleaned_data
            city = models.City.objects.filter(name__iexact=data.get('name'), state=state_response).first()
            if not city:
                city = city_form.save()
            return True, city
        else:
            errors = parse_error(city_form.errors, row)
            return False, errors
    else:
        return state_status, state_response


def get_institute_group(group_key, row):
    if not models.InstituteGroup.objects.filter(key=group_key).exists():
        return False, [{'key': 'institute_group',
                        'error': group_key + ' does not exists please create it first. key must be case sensitive ' + 'row number '
                                                                                                                      'is ' + str(
                            row)}]
    return True, None


def get_pathway_group(group_key, row):
    if not models.PathwayGroup.objects.filter(key=group_key).exists():
        return False, [{'key': 'pathway_group',
                        'error': group_key + ' does not exists please create it first.key must be case sensitive ' + 'row number '
                                                                                                                     'is ' + str(
                            row)}]
    return True, None


def get_apply_portal(data, row):
    if data.get(headers.APPLY_PORTAL):
        apply_portal = data.get(headers.APPLY_PORTAL).strip()
        apply_portal = models.ApplyPortal.objects.filter(key=apply_portal).first()
        if not apply_portal:
            errors = [{'key': 'apply_portal',
                       'error': data.get(headers.APPLY_PORTAL) + ' given apply portal key does not exists, first '
                                                                 'create this apply portsl in admin panel' + ' row '
                                                                                                             'number is ' + str(
                           row)}]
            return False, errors
        return True, apply_portal

    else:
        return True, None


def get_institute(institute_name, row):
    institute = models.Institute.objects.filter(institute_name=institute_name).first()
    if institute:
        return True, institute
    else:
        institute = models.Institute.objects.filter(institute_name__iexact=institute_name).first()
        if institute:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': institute.institute_name + ' already exists.Institute Name  must be case sensitive ' + institute_name + ' in row number ' + str(
                                row)}]
        return True, None


def get_campus(campus_name, institute, city, row):
    campus_name = campus_name.strip()
    city = city.strip()
    campus = models.InstituteCampus.objects.filter(campus=campus_name,
                                                   city__name=city,
                                                   institute=institute).first()
    if institute:
        return True, campus
    else:
        campus = models.InstituteCampus.objects.filter(campus__exact=campus, institute=institute,
                                                       city__name__exact=city).first()
        if institute:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': campus.campus + ' already exists.Institute Campus Name  must be case sensitive ' + campus + ' in row number ' + str(
                                row)}]
        return True, None


def create_or_get_institute_campus(data, row):
    if data.get(headers.INSTITUTE_NAME) and data.get(headers.CITY) and data.get(headers.INSTITUTE_CAMPUS):
        institute_name = data.get(headers.INSTITUTE_NAME).strip()
        data[headers.INSTITUTE_NAME] = institute_name
        institute_status, institute_response = get_institute(institute_name, row)
        if not institute_status:
            return institute_status, institute_response
        if institute_response:
            campus_status, campus_response = get_campus(data.get(headers.INSTITUTE_CAMPUS), institute_response,
                                                        data.get(headers.CITY), row)
            if not campus_status:
                return campus_status, campus_response
            if campus_response:
                return True, campus_response
    if data.get(headers.INSTITUTE_GROUP):
        group_status, group_response = get_institute_group(data.get(headers.INSTITUTE_GROUP), row)
        if not group_status:
            return False, group_response

    if data.get(headers.INSTITUTE_PATHWAY_GROUP):
        pathway_group_status, pathway_group_response = get_pathway_group(data.get(headers.INSTITUTE_PATHWAY_GROUP), row)
        if not pathway_group_status:
            return False, pathway_group_response

    if data.get(headers.APPLY_PORTAL):
        apply_portal_status, apply_portal_response = get_apply_portal(data, row)
        if not apply_portal_status:
            return False, apply_portal_response

    institute_form = forms.InstituteForm(data)
    if institute_form.is_valid():
        institute_data = institute_form.cleaned_data
        institute = models.Institute.objects.filter(institute_name=institute_data.get('institute_name')).first()
        if not institute:
            institute = institute_form.save()
        ranking_status, ranking_response = create_or_get_institute_ranking(data, institute, row)
        if not ranking_status:
            return False, ranking_response
    else:
        return False, parse_error(institute_form.errors, row)

    city_status, city_response = create_or_get_city(data, row)
    if city_status:
        institute_campus_form = forms.InstituteCampusForm(data, initial={'city': city_response,
                                                                         'institute': institute})
        if institute_campus_form.is_valid():
            institute_campus_data = institute_campus_form.cleaned_data
            campus = models.InstituteCampus.objects.filter(campus=institute_campus_data.get('campus'),
                                                           city=institute_campus_data.get('city'),
                                                           institute=institute).first()
            if not campus:
                campus = institute_campus_form.save()
            return True, campus
        else:
            return False, parse_error(institute_campus_form.errors, row)
    return city_status, city_response


def create_or_get_institute_ranking(data, institute, row):
    rankings = []
    if data.get(headers.QAS_WORLD_RANKING):
        rankings.append({'ranking_type': headers.QAS_WORLD_RANKING, 'value': data.get(headers.QAS_WORLD_RANKING)})
    if data.get(headers.US_NEWS_WORLD_RANKING):
        rankings.append(
            {'ranking_type': headers.US_NEWS_WORLD_RANKING, 'value': data.get(headers.US_NEWS_WORLD_RANKING)})
    if data.get(headers.US_NEWS_NATIONAL_RANKING):
        rankings.append(
            {'ranking_type': headers.US_NEWS_NATIONAL_RANKING, 'value': data.get(headers.US_NEWS_NATIONAL_RANKING)})
    if data.get(headers.TIMES_HIGHER_WORLD_RANKING):
        rankings.append(
            {'ranking_type': headers.TIMES_HIGHER_WORLD_RANKING, 'value': data.get(headers.TIMES_HIGHER_WORLD_RANKING)})
    if data.get(headers.SHANGHAI_RANKING):
        rankings.append({'ranking_type': headers.SHANGHAI_RANKING, 'value': data.get(headers.SHANGHAI_RANKING)})
    if len(rankings):
        for ranking in rankings:
            institute_ranking_form = forms.InstituteRankingForm(ranking, initial={'institute': institute})
            if institute_ranking_form.is_valid():
                institute_ranking_data = institute_ranking_form.cleaned_data
                institute_ranking, status = models.InstituteRanking.objects.update_or_create(
                    institute=institute_ranking_data.get('institute'),
                    ranking_type=institute_ranking_data.get('ranking_type'),
                    value=institute_ranking_data.get('value'),
                    defaults=institute_ranking_data)
            else:
                errors = parse_error(institute_ranking_form.errors, row)
                return False, errors
        return True, None
    else:
        return True, None


def get_discipline(data, row):
    if data.get(headers.DISCIPLINE):
        discipline = models.Discipline.objects.filter(key=data.get(headers.DISCIPLINE).strip()).first()
        if not discipline:
            errors = [{'key': 'discipline',
                       'error': data.get(
                           headers.DISCIPLINE) + ' given discipline key does not exists, first create this discipline in admin panel  ' + ' in row ' + str(
                           row)}]
            return False, errors
        return True, discipline

    else:
        errors = [{'key': 'discipline', 'error': ' discipline is required' + ' row number is ' + str(row)}]
        return False, errors


def get_degree_level(data, row):
    if data.get(headers.DEGREE_LEVEL):
        degree_level = models.DegreeLevel.objects.filter(key=data.get(headers.DEGREE_LEVEL).strip()).first()
        if not degree_level:
            errors = [{'key': 'degree_level',
                       'error': data.get(headers.DEGREE_LEVEL) + ' given degree level key does not exists, first '
                                                                 'create this degree level in admin panel' + ' row '
                                                                                                             'number is ' + str(
                           row)}]
            return False, errors
        return True, degree_level

    else:
        errors = [{'key': 'degree_level', 'error': ' degree_level is required' + ' row number is ' + str(row)}]
        return False, errors


def get_course_title(data, row):
    if data.get(headers.COURSE_TITLE):
        course_title_key = data.get(headers.COURSE_TITLE)
        course_title_key = course_title_key.strip()
        course_title = models.CourseTitle.objects.filter(key=course_title_key).first()
        if not course_title:
            errors = [{'key': 'course_title',
                       'error': data.get(headers.COURSE_TITLE) + ' given course_title key does not exists, first '
                                                                 'create this Course Title in admin panel ' + ' row '
                                                                                                              'number is ' + str(
                           row)}]
            return False, errors
        return True, course_title

    else:
        errors = [{'key': 'course_title', 'error': ' course_title is required' + ' row number is ' + str(row)}]
        return False, errors


def create_or_get_specialization(data, row):
    specialization_form = forms.SpecializationForm(data)
    if specialization_form.is_valid():
        data = specialization_form.cleaned_data
        specialization = models.Specialization.objects.filter(name=data.get('name')).first()
        if not specialization:
            specialization = specialization_form.save()
        return True, specialization
    else:
        errors = parse_error(specialization_form.errors, row)
        return False, errors


def get_discipline_degree_level_title_specialization(data, row):
    discipline_status, discipline_response = get_discipline(data, row)
    if discipline_status:
        degree_level_status, degree_level_response = get_degree_level(data, row)
        if degree_level_status:
            course_title_status, course_title_response = get_course_title(data, row)
            if course_title_status:
                specialization_status, specialization_response = create_or_get_specialization(data, row)
                if specialization_status:
                    return True, {headers.DISCIPLINE: discipline_response, headers.DEGREE_LEVEL: degree_level_response,
                                  headers.COURSE_TITLE: course_title_response,
                                  headers.COURSE_SPECIALIZATION: specialization_response}
                else:
                    return specialization_status, specialization_response

            else:
                return course_title_status, course_title_response

        else:
            return degree_level_status, degree_level_response
    else:
        return discipline_status, discipline_response


def create_or_update_course(data, campus, response, row):
    durations_status, durations_response = get_durations_list(data, row)
    if not durations_status:
        return durations_status, durations_response
    course_form = forms.CourseForm(data,
                                   initial={headers.DISCIPLINE: response.get(headers.DISCIPLINE),
                                            'campus': campus,
                                            # 'base_fee': 0,
                                            headers.COURSE_SPECIALIZATION: response.get(
                                                headers.COURSE_SPECIALIZATION),
                                            headers.COURSE_TITLE: response.get(headers.COURSE_TITLE),
                                            headers.DEGREE_LEVEL: response.get(headers.DEGREE_LEVEL)})
    if course_form.is_valid():
        form_data = course_form.cleaned_data
        # new

        course = models.Course.objects.filter(
            name=form_data.get('name'),
            campus=campus,
            discipline=form_data.get(headers.DISCIPLINE),
            degree_level=form_data.get(headers.DEGREE_LEVEL),
            course_title=form_data.get(headers.COURSE_TITLE),
            specialization=form_data.get(headers.COURSE_SPECIALIZATION),
            courseduration__type=durations_response.get('type'),
            courseduration__duration_one=durations_response.get('duration_one'),
            courseduration__duration_two=durations_response.get('duration_two'),
            courseduration__duration_three=durations_response.get('duration_three'),
        ).first()
        if course:
            models.Course.objects.filter(pk=course.pk).update(**form_data)
            # course.update(**form_data)
        else:
            course = course_form.save()

        # course, course_status = models.Course.objects.update_or_create(
        #     name=form_data.get('name'),
        #     campus=campus,
        #     discipline=form_data.get(headers.DISCIPLINE),
        #     degree_level=form_data.get(headers.DEGREE_LEVEL),
        #     course_title=form_data.get(headers.COURSE_TITLE),
        #     specialization=form_data.get(headers.COURSE_SPECIALIZATION),
        #     courseduration__type=durations_response.get('type'),
        #     courseduration__duration_one=durations_response.get('duration_one'),
        #     courseduration__duration_two=durations_response.get('duration_two'),
        #     courseduration__duration_three=durations_response.get('duration_three'),
        #     defaults=form_data)

        course_durations_status, course_durations_response = create_or_update_course_durations(data, course, row)
        if not course_durations_status:
            return course_durations_status, course_durations_response

        admission_schedule_status, admission_schedule_response = create_or_update_admission_schedule(
            data,
            course, row)
        if not admission_schedule_status:
            return admission_schedule_status, admission_schedule_response

        fee_status, fee_response = create_or_update_fee(data, course, row)
        if not fee_status:
            return fee_status, fee_response

        web_links_status, web_links_response = create_or_update_web_links(data, course, row)
        if not web_links_status:
            return web_links_status, web_links_response

        exam_status, exam_response = create_or_update_course_exams(data, course, row)
        if not exam_status:
            return exam_status, exam_response

        return True, None
    else:
        errors = parse_error(course_form.errors, row)
        return False, errors


def get_durations(duration):
    durations = {}
    if isinstance(duration, str):
        try:
            d_list = [float(d.strip()) for d in duration.split(",")]
        except ValueError:
            return False, 'duration must be numbers or points with "," separated '

        if len(d_list) > 3:
            return False, 'durations list can not be more than 3'
        for index in range(len(d_list)):
            if index == 0:
                durations['duration_one'] = d_list[index]
            if index == 1:
                durations['duration_two'] = d_list[index]
            if index == 2:
                durations['duration_three'] = d_list[index]

        return True, durations

    if isinstance(duration, int):
        durations['duration_one'] = duration
    if isinstance(duration, float):
        durations['duration_one'] = duration
    return True, durations


def get_durations_list(data, row):
    durations = None
    if data.get(headers.DURATION_YEARS):
        year_duration_status, year_duration_response = get_durations(data.get(headers.DURATION_YEARS))
        if not year_duration_status:
            return False, [{'key': headers.DURATION_YEARS,
                            'error': '' + year_duration_response + '' + ' and  row number is ' + str(row)}]
        year_duration_response['type'] = 'year'
        durations = year_duration_response

    if data.get(headers.PATHWAY_DURATION_SEMESTERS):
        semester_duration_status, semester_duration_response = get_durations(
            data.get(headers.PATHWAY_DURATION_SEMESTERS))
        if not semester_duration_status:
            return False, [{'key': headers.PATHWAY_DURATION_SEMESTERS,
                            'error': '' + semester_duration_response + '' + ' and  row number is ' + str(row)}]
        semester_duration_response['type'] = 'semester'
        durations = semester_duration_response
    if durations:
        return True, durations
    else:
        return False, [{'key': headers.DURATION_YEARS + ' or ' + headers.PATHWAY_DURATION_SEMESTERS,
                        'error': ' duration is required against this course ' + str(row)}]


def create_or_update_course_durations(data, course, row):
    durations_status, durations_response = get_durations_list(data, row)
    if durations_status:
        course_durations_form = forms.CourseDurationForm(durations_response, initial={'course': course})
        if course_durations_form.is_valid():
            form_data = course_durations_form.cleaned_data
            course_duration, status = models.CourseDuration.objects.update_or_create(course=form_data.get('course'),
                                                                                     type=form_data.get('type'),
                                                                                     defaults=form_data)
        else:
            errors = parse_error(course_durations_form.errors, row)
            return False, errors
        return True, None
    else:
        return durations_status, durations_response


def get_currency(currency_key, row):
    if currency_key:
        currency = models.Currency.objects.filter(key=currency_key).first()
        if not currency:
            errors = [{'key': 'currency',
                       'error': currency_key + ' given currency key does not exists, first '
                                               'add this currency' + 'row '
                                                                     'number is ' + str(row)}]
            return False, errors
        return True, currency

    else:
        errors = [{'key': 'currency', 'error': 'currency is required' + ' row number is ' + str(row)}]
        return False, errors


def get_fee_list(fee_type, fee, row):
    if isinstance(fee, str):
        fee_list = fee.strip().split('-')
        fee_list = list(filter(None, fee_list))
        if len(fee_list) == 1:
            try:
                fee_ceil_value = float(fee_list[0])
            except ValueError:
                return False, [{'key': fee_type,
                                'error': str(fee) + ' given invalid fee amount  in row number ' + str(row)}]

            return True, {'type': fee_type, 'ceil_value': fee_ceil_value}
        elif len(fee_list) == 2:

            try:
                fee_ceil_value = float(fee_list[0])
                fee_floor_value = float(fee_list[1])
            except ValueError:
                return False, [{'key': fee_type,
                                'error': str(fee) + ' given invalid fee amount  in row number ' + str(row)}]

            return True, {'type': fee_type, 'ceil_value': fee_ceil_value, 'floor_value': fee_floor_value}
        else:
            return False, [{'key': fee_type,
                            'error': str(fee) + ' given invalid amount  in row number ' + str(row)}]

    elif isinstance(fee, float) or isinstance(fee, int):
        return True, {'type': fee_type, 'ceil_value': fee}
    return False, [{'key': fee_type,
                    'error': str(fee) + ' given invalid amount in row number ' + str(row)}]


def create_or_update_fee(data, course, row):
    currency_status, currency_response = get_currency(data.get(headers.CURRENCY), row)
    if not currency_status:
        return False, currency_response
    fees = []
    if data.get(headers.FEE_PER_YEAR):
        fee_per_year_status, fee_per_year_response = get_fee_list(headers.FEE_PER_YEAR, data.get(headers.FEE_PER_YEAR),
                                                                  row)
        if not fee_per_year_status:
            return fee_per_year_status, fee_per_year_response
        fees.append(fee_per_year_response)
    if data.get(headers.TOTAL_PATHWAY_FEE):
        total_pathway_fee_status, total_pathway_fee_response = get_fee_list(headers.TOTAL_PATHWAY_FEE,
                                                                            data.get(headers.TOTAL_PATHWAY_FEE),
                                                                            row)
        if not total_pathway_fee_status:
            return total_pathway_fee_status, total_pathway_fee_response
        fees.append(total_pathway_fee_response)
    if data.get(headers.DIRECT_ENTRY_FEE_PER_SEMESTER):
        direct_entry_fee_status, direct_entry_fee_response = get_fee_list(headers.DIRECT_ENTRY_FEE_PER_SEMESTER,
                                                                          data.get(
                                                                              headers.DIRECT_ENTRY_FEE_PER_SEMESTER),
                                                                          row)
        if not direct_entry_fee_status:
            return direct_entry_fee_status, direct_entry_fee_response
        fees.append(direct_entry_fee_response)

    if data.get(headers.APPLICATION_FEE_REQUIRED) == 'yes':
        fees.append(
            {'type': 'application_fee', 'value': data.get(headers.APPLICATION_FEE_AMOUNT)})
    if data.get(headers.APPLICATION_FEE_REQUIRED) == 'no':
        fees.append(
            {'type': 'application_fee'})
    for fee in fees:
        fee_form = forms.FeeForm(fee, initial={'course': course, 'currency': currency_response})
        if fee_form.is_valid():
            form_data = fee_form.cleaned_data
            if models.CourseFee.objects.filter(course__id=course.id,
                                               type=form_data.get('type'),
                                               ceil_value=form_data.get('ceil_value'),
                                               currency=form_data.get('currency'),
                                               ).exists():
                models.CourseFee.objects.filter(
                                               course__id=course.id,
                                               type=form_data.get('type'),
                                               ceil_value=form_data.get('ceil_value'),
                                               currency=form_data.get('currency')
                ).update(**form_data)
            else:
                fee_form.save()
            # fee, status = models.CourseFee.objects.update_or_create(
            #     course=form_data.get('course'),
            #     type=form_data.get('type'),
            #     ceil_value=form_data.get('ceil_value'),
            #     currency=form_data.get('currency'),
            #     defaults=form_data)
        else:
            errors = parse_error(fee_form.errors, row)
            return False, errors
    return True, None


def create_or_update_web_links(data, course, row):
    apply_links = []
    if data.get(headers.COURSE_APPLY_WEB_LINK):
        apply_links.append({'type': headers.COURSE_APPLY_WEB_LINK, 'url': data.get(headers.COURSE_APPLY_WEB_LINK)})
    if data.get(headers.COURSE_FEE_WEB_LINK):
        apply_links.append({'type': headers.COURSE_FEE_WEB_LINK, 'url': data.get(headers.COURSE_FEE_WEB_LINK)})
    if data.get(headers.COURSE_DETAIL_WEB_LINK):
        apply_links.append({'type': headers.COURSE_DETAIL_WEB_LINK, 'url': data.get(headers.COURSE_DETAIL_WEB_LINK)})
    for apply_link in apply_links:
        web_links_form = forms.CourseWebLinkForm(apply_link, initial={'course': course})
        if web_links_form.is_valid():
            form_data = web_links_form.cleaned_data
            if models.CourseApply.objects.filter(course__id=course.id).exists():
                models.CourseApply.objects.filter(course__id=course.id).update(**form_data)
            else:
                web_links_form.save()
            # print(form_data)
            # web_links, status = models.CourseApply.objects.update_or_create(course=form_data.get('course'),
            #                                                                 type=form_data.get('type'),
            #                                                                 defaults=form_data)
        else:
            # print(web_links_form.cleaned_data)
            print('form invalid course web link')
            # errors = parse_error(web_links_form.errors, row)
            # return False, errors
    return True, None


def get_extra_columns(data):
    for column in headers.COMMON_HEADER:
        if column in data.keys():
            del data[column]
    return data


def create_or_update_course_exams(data, course, row):
    exams = []
    if data.get(headers.SAT1_REQUIRED):
        if data.get(headers.SAT1_REQUIRED) == 'yes':
            exams.append({'exam_type': 'sat1', 'required': True, 'score': data.get(headers.SAT1_SCORE)})
        if data.get(headers.SAT1_REQUIRED) == 'no':
            exams.append({'exam_type': 'sat1', 'required': False, 'score': None})
    if data.get(headers.SAT2_REQUIRED):
        if data.get(headers.SAT2_REQUIRED) == 'yes':
            exams.append({'exam_type': 'sat2', 'required': True, 'score': data.get(headers.SAT2_SCORE)})
        if data.get(headers.SAT2_REQUIRED) == 'no':
            exams.append({'exam_type': 'sat2', 'required': False, 'score': None})
    if data.get(headers.ACT_REQUIRED):
        if data.get(headers.ACT_REQUIRED) == 'yes':
            exams.append({'exam_type': 'act', 'required': True, 'score': data.get(headers.ACT_SCORE)})
        if data.get(headers.ACT_REQUIRED) == 'no':
            exams.append({'exam_type': 'act', 'required': False, 'score': None})
    if data.get(headers.GRE_REQUIRED):
        if data.get(headers.GRE_REQUIRED) == 'yes':
            exams.append({'exam_type': 'gre', 'required': True, 'score': data.get(headers.GRE_SCORE)})
        if data.get(headers.GRE_REQUIRED) == 'no':
            exams.append({'exam_type': 'gre', 'required': False, 'score': None})

    if data.get(headers.GMAT_REQUIRED):
        if data.get(headers.GMAT_REQUIRED) == 'yes':
            exams.append({'exam_type': 'gmat', 'required': True, 'score': data.get(headers.GMAT_SCORE)})
        if data.get(headers.GMAT_REQUIRED) == 'no':
            exams.append({'exam_type': 'gmat', 'required': False, 'score': None})

    if data.get(headers.IELTS_REQUIRED):
        if data.get(headers.IELTS_REQUIRED) == 'yes':
            exams.append({'exam_type': 'ielts', 'required': True, 'score': data.get(headers.IELTS_SCORE)})
        if data.get(headers.GMAT_REQUIRED) == 'no':
            exams.append({'exam_type': 'ielts', 'required': False, 'score': None})
    for exam in exams:
        exam_form = forms.CourseExamForm(exam, initial={'course': course})
        if exam_form.is_valid():
            form_data = exam_form.cleaned_data
            web_links, status = models.CourseExam.objects.update_or_create(course=form_data.get('course'),
                                                                           exam_type=form_data.get('exam_type'),
                                                                           defaults=form_data)
        else:
            errors = parse_error(exam_form.errors, row)
            return False, errors
    return True, None
