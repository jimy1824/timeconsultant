from model_utils import Choices
from constructor.helper import headers

INSTITUTE_TYPES = Choices(
    ('COLLEGE', 'College'),
    ('UNIVERSITY', 'University'),
    ('TAFE', 'TAFE College'),
    ('PATHWAY_COLLEGE', 'Pathway College'),
    ('PATHWAY_UNIVERSITY', 'Pathway University'),
)

SECTOR = Choices(
    ('PUBLIC', 'Public'),
    ('PRIVATE', 'Private'),
)

INSTITUTE_PANEL = Choices(
    ('p1', 'P1'),
    ('p2', 'P2'),
    ('p3', 'P3'),
)
DECISION = Choices(
    ('tbc', 'TBC'),
    ('yes', 'Yes'),
    ('no', 'No'),
)

INSTITUTE_RANKING_TYPE = Choices(
    (headers.QAS_WORLD_RANKING, ' QS World University Rankings'),
    (headers.TIMES_HIGHER_WORLD_RANKING, 'Times Higher Education World University Rankings'),
    (headers.US_NEWS_WORLD_RANKING, 'US News Global Universities Rankings'),
    (headers.SHANGHAI_RANKING, 'Shanghai Rankings'),
    (headers.US_NEWS_NATIONAL_RANKING, 'Shanghai Rankings'),
    (headers.TCF_RANKING, 'TCF Rankings'),
)

INSTITUTE_ACCEPTING_TYPE = Choices(
    (headers.INSTITUTE_ACCEPTANCE_RATIO_BACHELOR, ' Bachelor'),
    (headers.INSTITUTE_ACCEPTANCE_RATIO_MASTER, 'Master'),
)

DURATION_TYPE = Choices(
    ('year', 'Year'),
    ('semester', 'Semester'),
)

FEE_TYPE = Choices(
    (headers.FEE_PER_YEAR, 'Per Year Fee'),
    ('application_fee', 'Application Fee'),
    ('no_application_fee', 'Application Fee not Required'),
    (headers.TOTAL_PATHWAY_FEE, 'Total Pathway Fee'),
    (headers.DIRECT_ENTRY_FEE_PER_SEMESTER, 'Direct Entry Fee Per Semester'),
)

APPLY_TYPE = Choices(
    (headers.COURSE_DETAIL_WEB_LINK, 'Course detail Web Link'),
    (headers.COURSE_FEE_WEB_LINK, 'Course Fee Web Link'),
    (headers.COURSE_APPLY_WEB_LINK, 'Course Apply Web Link'),
)
APPLY_PORTAL = Choices(
    ('uni_assist', 'Uni Assist'),
    ('direct', 'Direct'),
)

SEASONAL_TYPES = Choices(
    ('winter', 'Winter'),
    ('summer', 'Summer'),
    ('autumn', 'Autumn'),
    ('spring', 'Spring'),
    ('fall', 'Fall'),
)
DEADLINE_TYPE = Choices(
    ('winter', 'Winter'),
    ('summer', 'Summer'),
    ('autumn', 'Autumn'),
    ('spring', 'Spring'),
    ('fall', 'Fall'),
    ('other', 'Other'),
)

INTAKE_MONTHS = Choices(
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
)

EXAM_TYPE = (
    ('sat1', 'sat1'),
    ('sat2', 'sat2'),
    ('act', 'act'),
    ('gre', 'gre'),
    ('gmat', 'gmat'),
    ('ielts', 'ielts'),
    ('gpa', 'gpa'),
)

ENTRY = Choices(
    ('pathway', 'Pathway'),
    ('direct', 'Direct')
)

CURRENCY = Choices(
    ('USA', 'USA dollar'),
)

LANGUAGES = Choices(
    (1, 'EN', 'English'),
)

COUNTRY = (
    ("china", "China"),
    ("europe", "Europe"),
    ("other", "Other"),
    ("australia", "Australia"),
    ("turkey", "Turkey"),
    ("uk", "UK"),
    ("usa-pattren", "USA Pattren"),
    ("usa-pathway", "USA Pathway"),
)

MONTHS = [
    'january',
    'february',
    'March',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november'
]
