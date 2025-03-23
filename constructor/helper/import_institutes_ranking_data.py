from constructor.helper import headers
from constructor.helper.import_course_data import parse_header_error
from constructor import models
from constructor import forms


def ParseError(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


class InstituteRankingExcelToJsonParser:

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
                if isinstance(data[key], str):
                    data[key] = data[key].strip()
                    if len(data[key]) == 0:
                        data[key] = None

    def get_header(self):
        default_header = set(headers.RANKING_HEADER)
        difference = default_header.difference(set(self.header))
        if difference:
            return False, parse_header_error(list(difference))
        return True, None


def update_raking(data, row):
    status, response = update_institute_raking(data, row)
    if not status:
        return status, response
    return True, None


def update_institute_raking(data, row):
    if data.get(headers.INSTITUTE_NAME):

        institute_name = data.get(headers.INSTITUTE_NAME).strip()
        institute_instance = models.Institute.objects.filter(institute_name=institute_name).first()

        if institute_instance:
            if data.get(headers.QAS_WORLD_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.QAS_WORLD_RANKING,
                                                           row)
                if not status:
                    return False, response
            if data.get(headers.TIMES_HIGHER_WORLD_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.TIMES_HIGHER_WORLD_RANKING,
                                                           row)
                if not status:
                    return False, response

            if data.get(headers.US_NEWS_WORLD_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.US_NEWS_WORLD_RANKING,
                                                           row)
                if not status:
                    return False, response

            if data.get(headers.US_NEWS_NATIONAL_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.US_NEWS_NATIONAL_RANKING,
                                                           row)
                if not status:
                    return False, response

            if data.get(headers.SHANGHAI_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.SHANGHAI_RANKING,
                                                           row)
                if not status:
                    return False, response

            if data.get(headers.TCF_RANKING):
                status, response = create_or_update_raking(data, institute_instance, headers.TIMES_HIGHER_WORLD_RANKING,
                                                           row)
                if not status:
                    return False, response

            return True, institute_instance
        else:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': institute_name + ' institute does not exists. ' + 'row number is ' + str(row)}]

    else:
        return False, [{'key': headers.INSTITUTE_NAME,
                        'error': headers.INSTITUTE_NAME + ' is required field. ' + 'row number is ' + str(row)}]


def create_or_update_raking(data, institute_instance, raking_type, row):
    value = data.get(raking_type)
    if isinstance(value, str):
        value_string = ''.join(e for e in value if e.isalnum())
        if value_string:
            try:
                int(value_string)
            except ValueError:
                return False, [{'key': raking_type,
                                'error': data.get(
                                    raking_type) + ' is not valid ranking  value . ' + 'row number is ' + str(row)}]

        else:
            return True, institute_instance
    initial_params = {
        'ranking_type': raking_type,
        'institute': institute_instance,
        'value': data.get(raking_type)
    }
    ranking_form = forms.InstituteRankingImportForm(data, initial=initial_params)
    if ranking_form.is_valid():
        form_data = ranking_form.cleaned_data
        raking_instance = models.InstituteRanking.objects.filter(ranking_type=form_data.get('ranking_type'),
                                                                 institute=form_data.get('institute')).first()
        if not raking_instance:
            scholarship_instance = ranking_form.save()
            return True, scholarship_instance

        else:
            raking_instance.value = form_data.get('value')
            raking_instance.save()
            return True, raking_instance
    else:
        errors = ParseError(ranking_form.errors, row)
        return False, errors
