INSTITUTE_TYPE = 'type'
INSTITUTE_SECTOR = 'sector'
INSTITUTE_NAME = 'institute_name'
INSTITUTE_ESTABLISHED = 'established'
INSTITUTE_HEADERS = [
    INSTITUTE_NAME,
    'city',
    'state',
    'postal_code',
    'country',
    'address',
    'lat',
    'lng'
]
COURSE_NAME = 'course_name'
COURSE_specializations = 'specializations'
DEGREE_LEVEL = 'degree_level'
DEGREE_TITLE = 'degree_title'
DISCIPLINE = 'discipline'
DURATION = 'duration'
COURSE_HEADERS = [
    COURSE_NAME,
    COURSE_specializations,
    DISCIPLINE,
    DURATION,
]
DEADLINE = 'deadline'
INTAKE = 'intake_date'
APPLICATION_OPEN_DATE = 'application_open_date'
APPLICATION_CLOSE_DATE = 'application_close_date'
FEE_PER_YEAR = 'fee_per_year'
COMPLETE_COURSE_FEE = 'complete_course_fee'
EXTRA_SCHEDULE_HEADER = [
    'summer_intake',
    'autumn_intake',
    'winter_intake'
]
COURSE_WEB_LINK = 'course_web_link'
FEE_WEB_LINK = 'fee_web_link'
APPLY_WEB_LINK = 'apply_web_link'
APPLICATION_FEE = 'application_fee'
WEB_LINK_HEADERS = [
    COURSE_WEB_LINK,
    FEE_WEB_LINK,
    APPLY_WEB_LINK,
]
QAS_RANKING = 'qs_ranking'
TIMES_HIGHER_RANKING = 'times_higher_ranking'
US_NEWS_RANKING = 'us_news_ranking'

RANKING_HEADER = [
    QAS_RANKING,
    TIMES_HIGHER_RANKING,
    US_NEWS_RANKING
]

PATHWAY_ENTRY_REQUIREMENTS = 'pathway_entry_requirements'
PROGRESSION_DEGREES = 'progression_degrees'
PROGRESSION_UNIVERSITIES = 'progression_universities'
PATHWAY_HEADER = [PATHWAY_ENTRY_REQUIREMENTS, PROGRESSION_DEGREES, PROGRESSION_UNIVERSITIES]
IELTS_EXEMPTION_TEST_DETAILS = 'ielts_exemption_test_details'

SCHOLARSHIP_DETAILS = 'scholarship_details'

EXTRA_EUROPE_HEADER = ['apply_via_uni_assist_portal', 'apply_via_direct_uni_portal', 'english_taught',
                       'english_german_taught', ]

EXTRA_USA_UNIVERSITY_HEADER = ['recommendation_letters_no', 'sat_1_score', 'sat_2_score', 'act_score', 'gre_score',
                               'gmat_score']
EXTRA_USA_PATHWAY_HEADER = ['entry', 'gpa_requirements', 'gre_gmat_requiredment ', 'direct_entry_requirements',
                            'direct_entry_fee', IELTS_EXEMPTION_TEST_DETAILS]
