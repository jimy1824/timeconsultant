from constructor.helper import headers
from constructor.helper.import_course_data import parse_header_error
from constructor import models
from constructor import forms


def ParseError(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


class InstitutePanelExcelToJsonParser:

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
        header = [headers.INSTITUTE_NAME, headers.INSTITUTE_PANEL, headers.APPLY_PORTAL]
        default_header = set(header)
        difference = default_header.difference(set(self.header))
        if difference:
            return False, parse_header_error(list(difference))
        return True, None


def update_panel(data, row):
    status, response = update_institute_panels(data, row)
    if not status:
        return status, response
    return True, None


def update_institute_panels(data, row):
    if data.get(headers.INSTITUTE_NAME):

        institute_name = data.get(headers.INSTITUTE_NAME).strip()
        institute_instance = models.Institute.objects.filter(institute_name=institute_name).first()

        if institute_instance:
            if data.get(headers.APPLY_PORTAL):
                apply_portal_name = data.get(headers.APPLY_PORTAL).strip()
                apply_portal_instance = models.ApplyPortal.objects.filter(key=apply_portal_name).first()
                if apply_portal_instance:
                    institute_instance.apply_portal = apply_portal_instance
                    institute_instance.save()

                else:
                    return False, [{'key': headers.APPLY_PORTAL,
                                    'error': apply_portal_name + ' key does not exists. Add from admin panel ' + 'row number is ' + str(
                                        row)}]
            if data.get(headers.INSTITUTE_PANEL):
                panel_name = data.get(headers.INSTITUTE_PANEL).strip()
                panels = ['p1', 'p2', 'p3']
                if panel_name in panels:
                    institute_instance.institute_panel = panel_name
                    institute_instance.save()

                else:
                    return False, [{'key': headers.INSTITUTE_PANEL,
                                    'error': panel_name + ' not valid choice. choices may be p1,p2,p3 ' + 'row number is ' + str(
                                        row)}]

            return True, institute_instance
        else:
            return False, [{'key': headers.INSTITUTE_NAME,
                            'error': institute_name + ' institute does not exists. ' + 'row number is ' + str(row)}]

    else:
        return False, [{'key': headers.INSTITUTE_NAME,
                        'error': headers.INSTITUTE_NAME + ' is required field. ' + 'row number is ' + str(row)}]
