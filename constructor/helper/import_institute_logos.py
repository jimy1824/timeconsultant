from constructor.helper import headers
from constructor.helper.import_course_data import parse_header_error
from constructor import models


class InstituteLogoExcelToJsonParser:

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
        default_header = set(headers.INSTITUTE_LOGOES_HEADER)
        difference = default_header.difference(set(self.header))
        if difference:
            return False, parse_header_error(list(difference))
        return True, None


def update_logo(data, row):
    status, response = update_institute_logo(data, row)
    if not status:
        return status, response
    return True, None


def update_institute_logo(data, row):
    if data.get(headers.INSTITUTE_NAME) and data.get(headers.INSTITUTE_LOGO):

        institute_name = data.get(headers.INSTITUTE_NAME).strip()
        institute_instance = models.Institute.objects.filter(institute_name=institute_name).first()

        if institute_instance:
            institute_instance.logo = data.get(headers.INSTITUTE_LOGO)
            institute_instance.save()
            return True, institute_instance
        else:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': headers.INSTITUTE_NAME + ' is required field. ' + 'row number is ' + str(row)}]

    else:
        if data.get(headers.INSTITUTE_LOGO) is None:
            return False, [{'key': headers.INSTITUTE_LOGO,
                            'error': headers.INSTITUTE_LOGO + ' is required field. ' + 'row number is ' + str(row)}]

        if data.get(headers.INSTITUTE_LOGO) is None:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': headers.INSTITUTE_NAME + ' is required field. ' + 'row number is ' + str(row)}]
