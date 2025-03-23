import pandas as pd

from constructor.helper.schedule_helper import get_date
from constructor.models import Institute, DegreeLevel, Discipline, ScholarshipType, Scholarship, ScholarshipStartDate, \
    ScholarshipCloseDate, ScholarshipOrganization, Country
from constructor import forms
from constructor.helper import headers

SCHOLARSHIP_NAME = 'scholarship_name'
SCHOLARSHIP_CONTENT = 'scholarship_content'
SCHOLARSHIP_TYPE = 'scholarship_type'
SCHOLARSHIP_VALUE = 'scholarship_value'
SCHOLARSHIP_LINK = 'scholarship_link'
DEGREE_LEVEL = 'degree_level'
NATIONALITY = 'nationality'
SCHOLARSHIP_APPLICATION_OPEN_DATE = 'scholarship_application_open_date'
SCHOLARSHIP_DEADLINE = 'scholarship_deadline'
SCHOLARSHIP_ELIGIBILITY = 'scholarship_eligibility'
HOW_TO_APPLY = 'how_to_apply'
SCHOLARSHIP_COURSES = 'scholarship_courses'


def parse_header_error(errors):
    return [{'key': field,
             'error': ' Column does not exist in given file against ' + '(columns are case sensitive)'}
            for field in errors]


def parse_foreign_key_relation_error(key, value, row):
    return [{'key': key, 'error': value + ' does not exist please create this first ' + ' row number is ' + str(row)}]


def ParseError(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


class ScholarshipHeader:
    def __init__(self):
        self.header = (headers.INSTITUTE_NAME,
                       headers.COUNTRY,
                       SCHOLARSHIP_NAME,
                       SCHOLARSHIP_CONTENT,
                       SCHOLARSHIP_TYPE,
                       SCHOLARSHIP_VALUE,
                       SCHOLARSHIP_LINK,
                       DEGREE_LEVEL,
                       headers.DISCIPLINE,
                       headers.DEGREE_LEVEL,
                       NATIONALITY,
                       SCHOLARSHIP_APPLICATION_OPEN_DATE,
                       SCHOLARSHIP_DEADLINE,
                       SCHOLARSHIP_ELIGIBILITY,
                       HOW_TO_APPLY,
                       SCHOLARSHIP_COURSES,
                       headers.INSTITUTE_NAME_ORGANIZATIONAL_SCHOLARSHIP
                       )

    def get_header(self):
        return self.header


class ScholarshipExcelToJsonParser:
    # def __init__(self, file):
    #     self.df = pd.read_excel(file)
    #     self.df.columns = self.df.columns.str.replace('\n', '')
    #     self.df = self.df.fillna('None')
    #     self.header = self.df.columns.ravel()
    #     self.data = self.df.to_dict(orient='records')
    #     self.clean_data()

    def __init__(self, df):
        self.df = df
        self.df.columns = self.df.columns.str.replace('\n', '')
        self.df = self.df.fillna('None')
        self.header = self.df.columns.ravel()
        self.data = self.df.to_dict(orient='records')
        self.clean_data()

    def clean_data(self):
        for data in self.data:
            for key in data:
                if data[key] == 'None':
                    data[key] = None

    def get_header(self):
        default_header = set(ScholarshipHeader().get_header())
        difference = default_header.difference(set(self.header))
        if difference:
            return False, parse_header_error(list(difference))
        return True, None

    def get_data(self):
        status, difference = self.get_header()
        if status:
            row = 2
            for data in self.data:
                relation_status, relation_response = validate_foreign_key_relation(data, row)
                if relation_status:
                    scholarship_status, scholarship_response = create_or_update_scholarship(data, relation_response,
                                                                                            row)
                    if not scholarship_status:
                        return scholarship_status, scholarship_response

                    scholarship_open_date_status, scholarship_open_date_response = create_or_update_scholarship_open_date(
                        data, scholarship_response, row)
                    if not scholarship_status:
                        return scholarship_status, scholarship_open_date_response

                    scholarship_close_date_status, scholarship_close_date_response = create_or_update_scholarship_close_date(
                        data, scholarship_response, row)
                    if not scholarship_close_date_status:
                        return scholarship_close_date_status, scholarship_close_date_response

                else:
                    return relation_status, relation_response
                row = row + 1
                break
            return status, None
        else:
            return status, difference


def get_or_create_complete_scholarship(data, row):
    relation_status, relation_response = validate_foreign_key_relation(data, row)
    if relation_status:
        scholarship_status, scholarship_response = create_or_update_scholarship(data, relation_response,
                                                                                row)
        if not scholarship_status:
            return scholarship_status, scholarship_response

        scholarship_open_date_status, scholarship_open_date_response = create_or_update_scholarship_open_date(
            data, scholarship_response, row)
        if not scholarship_status:
            return scholarship_status, scholarship_open_date_response

        scholarship_close_date_status, scholarship_close_date_response = create_or_update_scholarship_close_date(
            data, scholarship_response, row)
        if not scholarship_close_date_status:
            return scholarship_close_date_status, scholarship_close_date_response

    else:
        return relation_status, relation_response
    return True, None


def validate_foreign_key_relation(data, row):
    institute = data.get(headers.INSTITUTE_NAME)
    country = data.get(headers.COUNTRY)
    organization = data.get(headers.INSTITUTE_NAME_ORGANIZATIONAL_SCHOLARSHIP)
    disciplines = data.get(headers.DISCIPLINE)
    disciplines_values_list = []
    degree_levels = data.get(headers.DEGREE_LEVEL)
    degree_levels_values_list = []
    scholarship_types = data.get(SCHOLARSHIP_TYPE)
    scholarship_types_values_list = []
    if country:
        country_name = country.strip()
        country = Country.objects.filter(name=country_name).first()
        if not country:
            return False, parse_foreign_key_relation_error(headers.COUNTRY, data.get(headers.COUNTRY),
                                                           row)
    else:
        return False, [{'key': headers.COUNTRY,
                        'error': ' Country is required field ' + ' in row number ' + str(row)}]

    if institute:
        institute = institute.strip()
        institute = Institute.objects.filter(institute_name=institute).first()
        if not institute:
            return False, parse_foreign_key_relation_error(headers.INSTITUTE_NAME, data.get(headers.INSTITUTE_NAME),
                                                           row)
    if organization:
        organization_name = organization.strip()
        organization = ScholarshipOrganization.objects.filter(name=organization_name, country=country).first()
        if not organization:
            organization = ScholarshipOrganization(name=organization_name, country=country)
            organization.save()
    # else:
    #     return False, [{'key': headers.INSTITUTE_NAME,
    #                     'error': ' Institute is required field ' + ' in row number ' + str(row)}]

    if disciplines:
        discipline_list = disciplines.split(',')
        discipline_list = list(filter(None, discipline_list))
        for discipline in discipline_list:
            discipline = discipline.strip()
            discipline_instance = Discipline.objects.filter(key=discipline).first()
            if not discipline_instance:
                return False, parse_foreign_key_relation_error(headers.DISCIPLINE, discipline, row)
            disciplines_values_list.append(discipline_instance)
    if degree_levels:
        degree_level_list = degree_levels.split(',')
        degree_level_list = list(filter(None, degree_level_list))
        for degree_level in degree_level_list:
            degree_level = degree_level.strip()
            degree_level_instance = DegreeLevel.objects.filter(key=degree_level).first()
            if not degree_level_instance:
                return False, parse_foreign_key_relation_error(DEGREE_LEVEL, degree_level, row)
            degree_levels_values_list.append(degree_level_instance)
    if scholarship_types:
        scholarship_type_list = scholarship_types.split(',')
        scholarship_type_list = list(filter(None, scholarship_type_list))
        for scholarship_type in scholarship_type_list:
            scholarship_type_instance = ScholarshipType.objects.filter(key=scholarship_type).first()
            if not scholarship_type_instance:
                return False, parse_foreign_key_relation_error(SCHOLARSHIP_TYPE, scholarship_type, row)
            scholarship_types_values_list.append(scholarship_type_instance)

    return True, {'institute': institute, 'institute_name_organizational_scholarship': organization,
                  'discipline': disciplines_values_list,
                  'degree_level': degree_levels_values_list,
                  'scholarship_type': scholarship_types_values_list}


def create_or_update_scholarship(data, initial_params, row):
    scholarship_form = forms.ScholarshipForm(data, initial=initial_params)
    if scholarship_form.is_valid():
        form_data = scholarship_form.cleaned_data
        scholarship_instance = Scholarship.objects.filter(scholarship_name=form_data.get('scholarship_name'),
                                                          institute=form_data.get('institute')).first()
        if not scholarship_instance:
            scholarship_instance = scholarship_form.save()
            return True, scholarship_instance

        else:
            scholarship_instance.scholarship_content = form_data.get('scholarship_content')
            scholarship_instance.scholarship_value = form_data.get('scholarship_content')
            scholarship_instance.nationality = form_data.get('nationality')
            scholarship_instance.scholarship_eligibility = form_data.get('scholarship_eligibility')
            scholarship_instance.how_to_apply = form_data.get('how_to_apply')
            scholarship_instance.scholarship_link = form_data.get('scholarship_link')
            scholarship_instance.scholarship_courses = form_data.get('scholarship_courses')
            scholarship_instance.institute = form_data.get('institute')
            scholarship_instance.institute_name_organizational_scholarship = form_data.get('institute_name_organizational_scholarship')
            scholarship_instance.save()
            scholarship_instance.scholarship_type.remove(*scholarship_instance.scholarship_type.all())
            scholarship_instance.discipline.remove(*scholarship_instance.discipline.all())
            scholarship_instance.degree_level.remove(*scholarship_instance.degree_level.all())
            scholarship_instance.scholarship_type.set(form_data.get('scholarship_type'))
            scholarship_instance.discipline.set(form_data.get('discipline'))
            scholarship_instance.degree_level.set(form_data.get('degree_level'))
            return True, scholarship_instance
    else:
        errors = ParseError(scholarship_form.errors, row)
        return False, errors


def get_dates_list(dates):
    dates_value_list = []
    date_list = dates.split(',')
    date_list = list(filter(None, date_list))
    for date in date_list:
        date_status, date_response = get_date(date)
        if not date_status:
            return date_status, date_response
        dates_value_list.append({'month': date_response.get('month'),
                                 'day': date_response.get('days'),
                                 'year': date_response.get('year')})
    return True, dates_value_list


def save_scholarship_open_date(data, scholarship, row):
    form = forms.ScholarshipStartDateForm(data, initial={'scholarship': scholarship})
    if form.is_valid():
        form_data = form.cleaned_data
        ScholarshipStartDate_status, ScholarshipStartDate_status_response = ScholarshipStartDate.objects.update_or_create(
            scholarship=form_data.get('scholarship'),
            month=form_data.get('month'),
            defaults=form_data)
        return True, None

    else:
        errors = ParseError(form.errors, row)
        return False, errors


def save_scholarship_close_date(data, scholarship, row):
    form = forms.ScholarshipCloseDateForm(data, initial={'scholarship': scholarship})
    if form.is_valid():
        form_data = form.cleaned_data
        scholarship_close_date_status, scholarship_close_date_response = ScholarshipCloseDate.objects.update_or_create(
            scholarship=form_data.get('scholarship'),
            month=form_data.get('month'),
            defaults=form_data)
        return True, None

    else:
        errors = ParseError(form.errors, row)
        return False, errors


def create_or_update_scholarship_open_date(data, scholarship, row):
    application_open_date = data.get(SCHOLARSHIP_APPLICATION_OPEN_DATE)
    if application_open_date:
        if not isinstance(application_open_date, str):
            return False, [{'key': SCHOLARSHIP_APPLICATION_OPEN_DATE,
                            'error': '' + str(
                                application_open_date) + 'not valid format  (excel date will not be accepted )  in  '
                                                         'row number ' + str(
                                row)}]

        status, responses = get_dates_list(application_open_date.strip())
        if not status:
            return False, [{'key': SCHOLARSHIP_APPLICATION_OPEN_DATE,
                            'error': '' + application_open_date + ' must be in proper format ' + str(
                                responses) + ' and row '
                                             'number '
                                             'is ' +
                                     str(
                                         row)}]
        for response in responses:
            update_status, update_response = save_scholarship_open_date(response, scholarship, row)
            if not update_status:
                return update_status, update_response

    return True, None


def create_or_update_scholarship_close_date(data, scholarship, row):
    application_close_date = data.get(SCHOLARSHIP_DEADLINE)
    if application_close_date:
        if not isinstance(application_close_date, str):
            return False, [{'key': SCHOLARSHIP_DEADLINE,
                            'error': '' + str(
                                application_close_date) + 'not valid format  (excel date will not be accepted )  in  '
                                                          ' row number ' + str(
                                row)}]

        status, responses = get_dates_list(application_close_date.strip())
        if not status:
            return False, [{'key': SCHOLARSHIP_DEADLINE,
                            'error': '' + application_close_date + ' must be in proper format. given data is  ' + str(
                                responses) + ' and row '
                                             'number '
                                             'is ' +
                                     str(
                                         row)}]
        for response in responses:
            update_status, update_response = save_scholarship_close_date(response, scholarship, row)
            if not update_status:
                return update_status, update_response

    return True, None
