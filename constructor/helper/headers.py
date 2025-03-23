# institute
INSTITUTE_NAME = 'institute_name'
# two types only ( university,college)
INSTITUTE_TYPE = 'institute_type'
# two sector (private, public)
INSTITUTE_SECTOR = 'sector'

INSTITUTE_ESTABLISHED = 'established'
INSTITUTE_DESCRIPTION = 'institute_description'
INSTITUTE_CAMPUS = 'campus'

COUNTRY = 'country'
STATE = 'state'
CITY = 'city'
REGION = 'region'
POSTEL_CODE = 'postal_code'
ADDRESS = 'address'
LAT = 'latitude'
Lng = 'longitude'
# location
LOCATION_HEADER = [
    COUNTRY,
    STATE,
    REGION,
    CITY,
    POSTEL_CODE,
    ADDRESS,
    LAT,
    Lng
]

# institute group ( russel_group,go8,lvy_league,u15,tu9)
INSTITUTE_GROUP = 'institute_group'

# institute pathway  group (into,cg,kaplan,navitas,oxford,study_group,)
INSTITUTE_PATHWAY_GROUP = 'pathway_group'

# institute panel ( they are three types p1,p2,p3 default p3)
INSTITUTE_PANEL = 'institute_panel'

# INSTITUTE RANKING
QAS_WORLD_RANKING = 'qs_world_ranking'
TIMES_HIGHER_WORLD_RANKING = 'times_higher_world_ranking'
US_NEWS_WORLD_RANKING = 'us_news_world_ranking'
US_NEWS_NATIONAL_RANKING = 'us_news_national_ranking'
SHANGHAI_RANKING = 'shanghai_ranking'
TCF_RANKING = 'tcf_ranking'

RANKING_HEADER = [
    QAS_WORLD_RANKING,
    TIMES_HIGHER_WORLD_RANKING,
    US_NEWS_WORLD_RANKING,
    US_NEWS_NATIONAL_RANKING,
    SHANGHAI_RANKING
]

# institute accepting ratio
INSTITUTE_NAME_ORGANIZATIONAL_SCHOLARSHIP = 'institute_name_organizational_scholarship'
INSTITUTE_ACCEPTANCE_RATIO_MASTER = 'institute_acceptance_ratio_master'
INSTITUTE_ACCEPTANCE_RATIO_BACHELOR = 'institute_acceptance_ratio_bachelor'

# Institute financial aid per year ( amount it should be in string format)
INSTITUTE_FINANCIAL_AID_PER_YEAR = 'institute_financial_aid_per_year'
INSTITUTE_SCHOLARSHIP_AMOUNT_PER_YEAR = 'institute_scholarship_amount_per_year'
#  true and false fo required
INSTITUTE_SCHOLARSHIP_SEPARATE_APPLICATION_REQUIRED = 'institute_scholarship_separate_application_required'

# institute scholarship criteria  paragraph
INSTITUTE_SCHOLARSHIP_CRITERIA = 'institute_scholarship_criteria'

# institute accommodation availability   true or false
INSTITUTE_ACCOMMODATION_AVAILABILITY = 'accommodation_availability'

# this institute include in common app university web portal or not yes or no
COMMONAPP_UNIVERSITY = 'commonapp_university'

# this institute include essay requirement yes or no for america university
ESSAY_REQUIREMENT = 'essay_requirement'

INSTITUTE_HEADERS = [
                        INSTITUTE_NAME,
                        INSTITUTE_TYPE,
                        INSTITUTE_SECTOR,
                        INSTITUTE_ESTABLISHED,
                        INSTITUTE_DESCRIPTION,
                        INSTITUTE_CAMPUS,
                        INSTITUTE_GROUP,
                        INSTITUTE_PATHWAY_GROUP,
                        INSTITUTE_PANEL,
                        INSTITUTE_ACCEPTANCE_RATIO_MASTER,
                        INSTITUTE_ACCEPTANCE_RATIO_BACHELOR,
                        INSTITUTE_FINANCIAL_AID_PER_YEAR,
                        INSTITUTE_SCHOLARSHIP_AMOUNT_PER_YEAR,
                        INSTITUTE_SCHOLARSHIP_SEPARATE_APPLICATION_REQUIRED,
                        INSTITUTE_SCHOLARSHIP_CRITERIA,
                        INSTITUTE_ACCOMMODATION_AVAILABILITY,
                        COMMONAPP_UNIVERSITY,
                        ESSAY_REQUIREMENT,
                    ] + LOCATION_HEADER + RANKING_HEADER

# COURSE
COURSE_NAME = 'course_name'
COURSE_DESCRIPTION = 'course_description'
COURSE_OVERVIEW = 'overview'
COURSE_STRUCTURE = 'structure'
COURSE_CAREER_PROSPECTS = 'career_prospects'
COURSE_SPECIALIZATION = 'specialization'
DEGREE_LEVEL = 'degree_level'
COURSE_TITLE = 'course_title'
DISCIPLINE = 'discipline'

# default language is english
COURSE_LANGUAGE = 'course_language'
#  some courses may be in two languages like english and german
COURSE_DUAL_MEDIUM = 'dual_medium'
# course_entry_requirement paragraph
COURSE_ENTRY_REQUIREMENT = 'course_entry_requirements'
RECOMMENDATION_LETTERS = 'recommendation_letters'

# progression degrees
PROGRESSION_DEGREES = 'progression_degrees'
PROGRESSION_UNIVERSITIES = 'progression_universities'
COURSE_SCHOLARSHIP_DETAILS = 'course_scholarship_details'
IELTS_WAIVER_TEST = 'ielts_waiver_test'
PATHWAY_OR_DIRECT_ENTRY = 'pathway_or_direct_entry'

COURSE_HEADERS = [
    COURSE_NAME,
    COURSE_DESCRIPTION,
    COURSE_OVERVIEW,
    COURSE_STRUCTURE,
    COURSE_CAREER_PROSPECTS,
    COURSE_SPECIALIZATION,
    DISCIPLINE,
    DEGREE_LEVEL,
    COURSE_TITLE,
    RECOMMENDATION_LETTERS,
    COURSE_ENTRY_REQUIREMENT,
    PROGRESSION_DEGREES,
    PROGRESSION_UNIVERSITIES,
    COURSE_SCHOLARSHIP_DETAILS,
    PATHWAY_OR_DIRECT_ENTRY,
    IELTS_WAIVER_TEST,
    COURSE_LANGUAGE
]
# course duration

# course duration in years and may be multiple
DURATION_YEARS = 'duration_years'
# pathway duration in semesters
PATHWAY_DURATION_SEMESTERS = 'pathway_duration_semesters'

COURSE_DURATION = [
    DURATION_YEARS,
    PATHWAY_DURATION_SEMESTERS
]

# course schedule

#  it may be date (dates may be multiple) and winter,summer,autumn
INTAKE = 'intake_month'
# INTAKE_SUMMER = 'intake_summer'
# INTAKE_WINTER = 'intake_winter'
# INTAKE_AUTUMN = 'intake_autumn'
# INTAKE_SPRING = 'intake_spring'
# INTAKE_FALL = 'intake_fall'

COURSE_INTAKE = [
    INTAKE,
    # INTAKE_SUMMER,
    # INTAKE_WINTER,
    # INTAKE_AUTUMN,
    # INTAKE_SPRING,
    # INTAKE_FALL
]

# deadline
DEADLINE = 'deadline_date'
# DEADLINE_SUMMER = 'deadline_summer'
# DEADLINE_WINTER = 'deadline_winter'
# DEADLINE_AUTUMN = 'deadline_autumn'
# DEADLINE_SPRING = 'deadline_spring'
# DEADLINE_FALL = 'deadline_fall'

COURSE_DEADLINE = [
    DEADLINE,
    # DEADLINE_SUMMER,
    # DEADLINE_WINTER,
    # DEADLINE_AUTUMN,
    # DEADLINE_SPRING,
    # DEADLINE_FALL
]

APPLICATION_OPEN_DATE = 'application_open_date'
# APPLICATION_CLOSE_DATE = 'application_close_date'

COURSE_SCHEDULE_HEADERS = [
    APPLICATION_OPEN_DATE,
    # APPLICATION_CLOSE_DATE,
]

# COURSE FEE

FEE_PER_YEAR = 'fee_per_year'
TOTAL_PATHWAY_FEE = 'total_pathway_fee'
DIRECT_ENTRY_FEE_PER_SEMESTER = 'direct_entry_fee_per_semester'
APPLICATION_FEE_REQUIRED = 'application_fee_required'
APPLICATION_FEE_AMOUNT = 'application_fee_amount'
CURRENCY = 'currency'

COURSE_FEE_HEADERS = [
    FEE_PER_YEAR,
    TOTAL_PATHWAY_FEE,
    DIRECT_ENTRY_FEE_PER_SEMESTER,
    APPLICATION_FEE_REQUIRED,
    APPLICATION_FEE_AMOUNT,
    CURRENCY,

]

# apply this links for admin only
# apply portal two types direct or uni_assist
APPLY_PORTAL = 'apply_portal'

COURSE_DETAIL_WEB_LINK = 'course_detail_web_link'
COURSE_FEE_WEB_LINK = 'course_fee_web_link'
COURSE_APPLY_WEB_LINK = 'course_apply_web_link'

WEB_LINK_HEADERS = [
    COURSE_DETAIL_WEB_LINK,
    COURSE_FEE_WEB_LINK,
    COURSE_APPLY_WEB_LINK,
    APPLY_PORTAL
]

# Exams
SAT1_REQUIRED = 'sat1_required'
SAT1_SCORE = 'sat1_score'

SAT2_REQUIRED = 'sat2_required'
SAT2_SCORE = 'sat2_score'

ACT_REQUIRED = 'act_required'
ACT_SCORE = 'act_score'

GRE_REQUIRED = 'gre_required'
GRE_SCORE = 'gre_score'

GMAT_REQUIRED = 'gmat_required'
GMAT_SCORE = 'gmat_score'

IELTS_REQUIRED = 'ielts_required'
IELTS_SCORE = 'ielts_score'
# gpa required minimum
GPA_REQUIRED = 'gpa_required'

EXAM_HEADERS = [
    SAT1_REQUIRED,
    SAT1_SCORE,
    SAT2_REQUIRED,
    SAT2_SCORE,
    ACT_REQUIRED,
    ACT_SCORE,
    GRE_REQUIRED,
    GRE_SCORE,
    GMAT_REQUIRED,
    GMAT_SCORE,
    IELTS_REQUIRED,
    IELTS_SCORE,
    GPA_REQUIRED
]

COMMON_HEADER = INSTITUTE_HEADERS + COURSE_HEADERS + COURSE_DURATION + COURSE_INTAKE + COURSE_DEADLINE + COURSE_SCHEDULE_HEADERS + COURSE_FEE_HEADERS + WEB_LINK_HEADERS

INSTITUTE_LOGO = 'logo'
INSTITUTE_LOGOES_HEADER = [INSTITUTE_NAME, INSTITUTE_LOGO]
