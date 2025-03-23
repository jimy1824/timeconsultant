from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import pandas as pd
from constructor import constant


class DataframeUtil(object):
    @staticmethod
    def get_validated_dataframe(path: str) -> pd.DataFrame:
        df = pd.read_excel(path, dtype=str, engine='openpyxl')
        df.columns = df.columns.str.lower()
        df = df.fillna(-1)
        return df.mask(df == -1, None)


def in_memory_file_to_temp(in_memory_file):
    path = default_storage.save('tmp/%s' % in_memory_file.name, ContentFile(in_memory_file.read()))
    return path


def ParseError(errors, row):
    return [{'key': k, 'error': v[0] + ' row number is ' + str(row)} for k, v in errors.items()]


def ParseHeaderError(errors, country):
    return [{'key': field,
             'error': ' Column does not exist in given file against ' + country + ' country (columns are case sensitive)'}
            for field in errors]


class CountryHeader():
    def __init__(self):
        self.headers = {}
        self.headers['china'] = (constant.INSTITUTE_HEADERS +
                                 [constant.INSTITUTE_SECTOR, constant.INSTITUTE_ESTABLISHED] +
                                 constant.COURSE_HEADERS +
                                 [constant.DEGREE_LEVEL, constant.DEGREE_TITLE, constant.INTAKE, constant.DEADLINE,
                                  constant.FEE_PER_YEAR, constant.FEE_WEB_LINK]
                                 )
        self.headers['other'] = (constant.INSTITUTE_HEADERS +
                                 [constant.INSTITUTE_TYPE, constant.INSTITUTE_SECTOR, constant.INSTITUTE_ESTABLISHED] +
                                 constant.COURSE_HEADERS +
                                 [constant.DEGREE_LEVEL, constant.DEGREE_TITLE, constant.INTAKE, constant.DEADLINE,
                                  constant.APPLICATION_FEE, constant.FEE_PER_YEAR] +
                                 constant.WEB_LINK_HEADERS +
                                 constant.RANKING_HEADER
                                 )
        self.headers['europe'] = (constant.INSTITUTE_HEADERS +
                                  [constant.INSTITUTE_TYPE, constant.INSTITUTE_SECTOR, constant.INSTITUTE_ESTABLISHED] +
                                  constant.COURSE_HEADERS + [constant.DEGREE_LEVEL, constant.DEGREE_TITLE] +
                                  [constant.DEADLINE, constant.FEE_PER_YEAR] +
                                  constant.EXTRA_SCHEDULE_HEADER +
                                  constant.WEB_LINK_HEADERS +
                                  constant.RANKING_HEADER +
                                  constant.EXTRA_EUROPE_HEADER)

        self.headers['turkey'] = (constant.INSTITUTE_HEADERS +
                                  [constant.INSTITUTE_SECTOR, constant.INSTITUTE_ESTABLISHED] +
                                  constant.COURSE_HEADERS + [constant.DEGREE_LEVEL, constant.DEGREE_TITLE] +
                                  [constant.INTAKE, constant.APPLICATION_OPEN_DATE, constant.APPLICATION_CLOSE_DATE,
                                   constant.FEE_PER_YEAR, constant.APPLICATION_FEE] +
                                  constant.WEB_LINK_HEADERS +
                                  constant.RANKING_HEADER +
                                  [constant.SCHOLARSHIP_DETAILS])

        self.headers['usa-pattren'] = (constant.INSTITUTE_HEADERS +
                                       [constant.INSTITUTE_TYPE] +
                                       constant.COURSE_HEADERS + [constant.DEGREE_LEVEL, constant.DEGREE_TITLE] +
                                       [constant.INTAKE, constant.DEADLINE, constant.FEE_PER_YEAR,
                                        constant.APPLICATION_FEE] +
                                       constant.WEB_LINK_HEADERS +
                                       constant.EXTRA_USA_UNIVERSITY_HEADER
                                       )

        self.headers['australia'] = (constant.INSTITUTE_HEADERS +
                                     [constant.INSTITUTE_TYPE] +
                                     [constant.COURSE_NAME, constant.COURSE_specializations, constant.DISCIPLINE,
                                      constant.DEGREE_TITLE] +
                                     [constant.INTAKE, constant.COMPLETE_COURSE_FEE] +
                                     [constant.COURSE_WEB_LINK, constant.FEE_WEB_LINK, constant.SCHOLARSHIP_DETAILS,
                                      constant.QAS_RANKING] +
                                     constant.PATHWAY_HEADER
                                     )

        self.headers['uk'] = (constant.INSTITUTE_HEADERS +
                              [constant.INSTITUTE_TYPE] +
                              [constant.COURSE_NAME, constant.COURSE_specializations, constant.DISCIPLINE,
                               constant.DEGREE_TITLE] +
                              [constant.INTAKE, constant.COMPLETE_COURSE_FEE] +
                              [constant.FEE_WEB_LINK, constant.SCHOLARSHIP_DETAILS,
                               constant.QAS_RANKING, constant.TIMES_HIGHER_RANKING] +
                              constant.PATHWAY_HEADER +
                              [constant.IELTS_EXEMPTION_TEST_DETAILS]
                              )

        self.headers['usa-pathway'] = (constant.INSTITUTE_HEADERS +
                                       [constant.COURSE_NAME, constant.COURSE_specializations, constant.DISCIPLINE,
                                        constant.DEGREE_LEVEL, constant.DURATION] +
                                       [constant.INTAKE, constant.COMPLETE_COURSE_FEE] +
                                       [constant.FEE_WEB_LINK, constant.SCHOLARSHIP_DETAILS,
                                        constant.US_NEWS_RANKING] +
                                       [constant.PATHWAY_ENTRY_REQUIREMENTS, constant.PROGRESSION_DEGREES, ] +
                                       constant.EXTRA_USA_PATHWAY_HEADER
                                       )

    def get_header(self, country):
        return self.headers.get(country)
