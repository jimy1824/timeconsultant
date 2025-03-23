from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator, MinLengthValidator
from common.models import TimeStampedModel
from .choices import (INSTITUTE_TYPES, SECTOR, INSTITUTE_PANEL, INSTITUTE_RANKING_TYPE, INSTITUTE_ACCEPTING_TYPE,
                      DURATION_TYPE,
                      FEE_TYPE, APPLY_TYPE, APPLY_PORTAL, SEASONAL_TYPES, INTAKE_MONTHS, DEADLINE_TYPE, ENTRY,
                      EXAM_TYPE,
                      CURRENCY, DECISION)

from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager
from django.db.models.query import QuerySet
from django_group_by import GroupByMixin


class CustomUser(AbstractUser):
    profile_img = models.ImageField(upload_to='profiles/images', blank=True, null=True)
    username = models.CharField(blank=True, null=True, max_length=250)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Region(TimeStampedModel):
    name = models.CharField(max_length=255, help_text="Region Name", verbose_name=" Region Name")

    def __str__(self):
        return f"{self.name}"


class Country(TimeStampedModel):
    name = models.CharField(max_length=255, help_text="Country Name", verbose_name="Country Name")
    logo = models.URLField(max_length=500, blank=True, null=True)
    icon = models.URLField(max_length=500, blank=True, null=True)
    short_description = models.TextField(help_text=" Country content", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=1)
    popular = models.BooleanField(default=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    scholarship_logo = models.URLField(max_length=700, blank=True, null=True)
    latitude = models.FloatField(help_text="latitude", blank=True, null=True)
    longitude = models.FloatField(help_text="longitude", blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}"

    @property
    def number_of_scholarships(self):
        return Scholarship.objects.filter(
            institute__institutecampus__city__state__country__id=self.id).distinct().count()


class State(TimeStampedModel):
    name = models.CharField(max_length=255, help_text="State Name", verbose_name="State Name")
    region = models.CharField(max_length=255, help_text="State Name", blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, )
    popular = models.BooleanField(default=False)
    latitude = models.FloatField(help_text="latitude", blank=True, null=True)
    longitude = models.FloatField(help_text="longitude", blank=True, null=True)

    def __str__(self):
        return f"{self.name}--{self.country.name}"

    class Meta:
        ordering = ('name',)


class City(TimeStampedModel):
    name = models.CharField(max_length=255, help_text="City Name", verbose_name=" City Name")
    description = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, )
    popular = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}--{self.state.name}--{self.state.country.name}"


class InstituteGroup(TimeStampedModel):
    key = models.CharField(unique=True, max_length=255, help_text="Group short Name key")
    display_name = models.CharField(max_length=255, help_text="Group Name")
    short_description = models.TextField(help_text=" Group content")
    content = models.TextField(help_text=" Group content")
    logo = models.URLField(max_length=500, blank=True, null=True)
    order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.display_name}"


class PathwayGroup(TimeStampedModel):
    key = models.CharField(unique=True, max_length=255, help_text="Group short Name key")
    display_name = models.CharField(max_length=255, help_text="Group Name")
    short_description = models.TextField(help_text=" Group content")
    description = models.TextField(help_text=" Group content")
    logo = models.URLField(max_length=500, blank=True, null=True)
    order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.display_name}"


class ApplyPortal(TimeStampedModel):
    key = models.CharField(unique=True, max_length=255, help_text="Apply portal short Name key")
    display_name = models.CharField(max_length=255, help_text="Apply Portal Name")
    short_description = models.TextField(help_text=" Group content")
    description = models.TextField(help_text=" Apply portal content")
    logo = models.URLField(max_length=500, blank=True, null=True)
    order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.display_name}"


class Institute(TimeStampedModel):
    institute_name = models.CharField(max_length=255, help_text="Institute Name", verbose_name="Institute Name")
    logo = models.URLField(max_length=500, blank=True, null=True)
    institute_type = models.CharField(choices=INSTITUTE_TYPES,
                                      max_length=25,
                                      default=INSTITUTE_TYPES.UNIVERSITY,
                                      help_text="Institute Type ie college or university")
    sector = models.CharField(choices=SECTOR,
                              default=SECTOR.PRIVATE,
                              max_length=25,
                              help_text="Institute sector ie public or private")
    institute_panel = models.CharField(choices=INSTITUTE_PANEL,
                                       default=INSTITUTE_PANEL.p3,
                                       max_length=25,
                                       help_text="Institute sector ie public or private")
    established = models.CharField(max_length=255, blank=True, null=True,
                                   help_text="Campus establish establish in which year")
    institute_short_description = models.TextField(blank=True, null=True)
    institute_description = models.TextField(blank=True, null=True)
    institute_group = models.ForeignKey(InstituteGroup, on_delete=models.CASCADE, blank=True, null=True)
    pathway_group = models.ForeignKey(PathwayGroup, on_delete=models.CASCADE, blank=True, null=True)
    apply_portal = models.ForeignKey(ApplyPortal, on_delete=models.CASCADE, blank=True, null=True)
    institute_financial_aid_per_year = models.CharField(max_length=255, blank=True, null=True)
    institute_scholarship_amount_per_year = models.CharField(max_length=255, blank=True, null=True)
    institute_scholarship_separate_application_required = models.CharField(choices=DECISION, default=DECISION.tbc,
                                                                           max_length=25)
    institute_scholarship_criteria = models.TextField(blank=True, null=True)
    accommodation_availability = models.CharField(choices=DECISION, default=DECISION.tbc,
                                                  max_length=25)
    commonapp_university = models.CharField(choices=DECISION, default=DECISION.tbc,
                                            max_length=25)
    essay_requirement = models.CharField(choices=DECISION, default=DECISION.tbc,
                                         max_length=25)

    def __str__(self):
        return f"{self.institute_name}"


class InstituteCampus(TimeStampedModel):
    campus = models.CharField(max_length=255, help_text="Institute Campus Name")
    city = models.ForeignKey(City, on_delete=models.CASCADE, )
    address = models.TextField(help_text="Full addresss")
    latitude = models.FloatField(help_text="latitude")
    longitude = models.FloatField(help_text="longitude")
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.campus}--{self.institute.institute_name}--{self.city.state.name}--{self.city.state.country.name}"


class InstituteRanking(TimeStampedModel):
    ranking_type = models.CharField(choices=INSTITUTE_RANKING_TYPE, max_length=100)
    value = models.CharField(max_length=255, )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.ranking_type}"


class InstituteAcceptingRatio(TimeStampedModel):
    accepting_type = models.CharField(choices=INSTITUTE_ACCEPTING_TYPE, max_length=100)
    value = models.CharField(max_length=255, )
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, )


class Discipline(TimeStampedModel):
    key = models.CharField(unique=True, max_length=100)
    name = models.CharField(unique=True, max_length=255, help_text="Discipline", verbose_name="Discipline Name")
    short_description = models.TextField(help_text=" Group content")
    description = models.TextField()
    logo = models.URLField(max_length=500, blank=True, null=True)
    icon = models.URLField(max_length=500, blank=True, null=True)
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}"


class SubDiscipline(TimeStampedModel):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, )
    key = models.CharField(unique=True, max_length=100)
    name = models.CharField(unique=True, max_length=255, help_text="Discipline Name")
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"


class Specialization(TimeStampedModel):
    name = models.CharField(max_length=255, help_text="Specialization Name", verbose_name="Specialization")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}"


class DegreeLevel(TimeStampedModel):
    UNDERGRADUATE = 'undergradute'
    POSTGRADUATE = 'postgradute'
    POSTGRADUATE_RESEARCH = 'postgradute_by_research'
    Degree_Level_CHOICES = [
        (UNDERGRADUATE, 'Undergradute'),
        (POSTGRADUATE, 'Postgradute'),
        (POSTGRADUATE_RESEARCH, 'Postgradute by Research'),
    ]
    level_type = models.CharField(
        max_length=50,
        choices=Degree_Level_CHOICES,
        default=UNDERGRADUATE,
    )
    key = models.CharField(unique=True, max_length=100)
    display_name = models.CharField(unique=True, max_length=255, help_text="DegreeLevel ie Bachelor,Master ",
                                    verbose_name="DegreeLevel")
    order = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.display_name}"


class CourseTitle(TimeStampedModel):
    key = models.CharField(unique=True, max_length=100)
    display_name = models.CharField(unique=True, max_length=255, help_text="Associate degree Title ie BA,Bsc,Bs")

    def __str__(self):
        return f"{self.display_name}"


class Currency(TimeStampedModel):
    key = models.CharField(unique=True, max_length=100)
    display_name = models.CharField(max_length=255, help_text="Currency must be unique", unique=True)
    description = models.CharField(max_length=255, help_text="Australian Dollar (AUD)")
    value_to_pkr = models.FloatField()

    def __str__(self):
        return f"{self.display_name}"


class Course(TimeStampedModel):
    logo = models.URLField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=255, help_text="Course Name")
    course_description = models.TextField(blank=True, null=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, )
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, )
    course_title = models.ForeignKey(CourseTitle, on_delete=models.CASCADE)
    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.CASCADE)
    course_language = models.CharField(max_length=100)
    total_credit_hours = models.CharField(max_length=100, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    structure = models.TextField(blank=True, null=True)
    career_prospects = models.TextField(blank=True, null=True)
    dual_medium = models.CharField(max_length=100, blank=True, null=True)
    course_entry_requirements = models.TextField(blank=True, null=True)
    progression_degrees = models.TextField(blank=True, null=True)
    progression_universities = models.TextField(blank=True, null=True)
    course_scholarship_details = models.TextField(blank=True, null=True)
    recommendation_letters = models.IntegerField(blank=True, null=True)
    entry = models.CharField(choices=ENTRY, max_length=25, blank=True, null=True)
    ielts_waiver_test = models.TextField(blank=True, null=True)
    # apply_portal = models.CharField(choices=APPLY_PORTAL, max_length=25, blank=True, null=True)
    campus = models.ForeignKey(InstituteCampus, on_delete=models.CASCADE, )
    base_fee = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name},{self.id}"


class CourseDuration(TimeStampedModel):
    type = models.CharField(choices=DURATION_TYPE,
                            max_length=25, )
    duration_one = models.FloatField()
    duration_two = models.FloatField(blank=True, null=True)
    duration_three = models.FloatField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.type}"


class CourseIntakeAndDeadLine(TimeStampedModel):
    intake_month = models.CharField(choices=INTAKE_MONTHS,
                                    max_length=25, blank=True, null=True)
    intake_day = models.IntegerField(validators=[
        MaxValueValidator(31),
        MinValueValidator(1)
    ], blank=True, null=True)
    intake_year = models.IntegerField(
        blank=True, null=True)

    deadline_day = models.IntegerField(validators=[
        MaxValueValidator(31),
        MinValueValidator(1)
    ], blank=True, null=True)

    deadline_months = models.CharField(choices=INTAKE_MONTHS,
                                       max_length=25, blank=True, null=True)

    deadline_year = models.IntegerField(
        blank=True, null=True)

    application_open_day = models.IntegerField(validators=[
        MaxValueValidator(31),
        MinValueValidator(1)
    ], blank=True, null=True)

    application_open_months = models.CharField(choices=INTAKE_MONTHS,
                                               max_length=25, blank=True, null=True)

    application_open_year = models.IntegerField(
        blank=True, null=True)
    rolling_intake = models.BooleanField(default=False, help_text="student can start studying any month ")
    rolling_deadline = models.BooleanField(default=False, help_text="student can apply for admission any time")

    course = models.ForeignKey(Course, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.intake_month}"


class CourseFee(TimeStampedModel):
    type = models.CharField(choices=FEE_TYPE, max_length=100, )
    ceil_value = models.FloatField(blank=True, null=True)
    floor_value = models.FloatField(blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, )


class CourseApply(TimeStampedModel):
    type = models.CharField(choices=APPLY_TYPE, max_length=25, blank=True, null=True)
    url = models.URLField(blank=True, null=True, max_length=5000)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, )


class CourseExam(TimeStampedModel):
    exam_type = models.CharField(choices=EXAM_TYPE, max_length=25, )
    required = models.BooleanField(default=False)
    score = models.FloatField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, )


class ScholarshipType(TimeStampedModel):
    key = models.CharField(unique=True, max_length=255, help_text="Scholarship Type short Name key")
    display_name = models.CharField(max_length=255, help_text="Scholarship Type display Name")

    def __str__(self):
        return f"{self.display_name}"


class ScholarshipOrganization(TimeStampedModel):
    name = models.CharField(max_length=750, help_text="Scholarship name")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, )
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Scholarship(TimeStampedModel):
    scholarship_name = models.CharField(max_length=500, help_text="Scholarship name")
    scholarship_content = models.TextField(blank=True, null=True)
    scholarship_type = models.ManyToManyField(ScholarshipType)
    scholarship_value = models.TextField()
    nationality = models.TextField()
    scholarship_eligibility = models.TextField(blank=True, null=True)
    how_to_apply = models.TextField(blank=True, null=True)
    scholarship_link = models.URLField(max_length=700, blank=True, null=True)
    discipline = models.ManyToManyField(Discipline)
    degree_level = models.ManyToManyField(DegreeLevel)
    scholarship_courses = models.TextField(blank=True, null=True)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, blank=True, null=True)
    institute_name_organizational_scholarship = models.ForeignKey(ScholarshipOrganization, on_delete=models.CASCADE,
                                                                  blank=True, null=True)

    class Meta:
        ordering = ('scholarship_name',)

    def __str__(self):
        return f"{self.scholarship_name}"


class ScholarshipStartDate(TimeStampedModel):
    month = models.CharField(choices=INTAKE_MONTHS,
                             max_length=25, )
    day = models.IntegerField(validators=[
        MaxValueValidator(31),
        MinValueValidator(1)
    ], blank=True, null=True)
    year = models.IntegerField(
        blank=True, null=True)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.month}"


class ScholarshipCloseDate(TimeStampedModel):
    month = models.CharField(choices=INTAKE_MONTHS,
                             max_length=25, )
    day = models.IntegerField(validators=[
        MaxValueValidator(31),
        MinValueValidator(1)
    ], blank=True, null=True)
    year = models.IntegerField(
        blank=True, null=True)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, )

    def __str__(self):
        return f"{self.month}"


class Blog(TimeStampedModel):
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    logo = models.URLField(max_length=1000, blank=True, null=True)
    heading = models.CharField(max_length=500)
    short_description = models.TextField(max_length=500)
    content = models.TextField()

    def __str__(self):
        return f"{self.heading}"


class DynamicPages(TimeStampedModel):
    PRIVACY = 'privacy'
    TERMS = 'terms'
    ABOUT_TCF = 'tcf_intro'
    CAREERS = 'Careers'
    CONTACT_US = 'contact'
    MARKETING_ADVERTISEMENT = 'marketing_advertisement'
    ENGLISH_PROGRAM = 'english_program_in_europe'
    CHEAPEST_MBA = 'cheapest_MBA'
    SUITABLE_PROGRAM_IN_UNI = 'suitable_program_in_uni'

    PAGES_TYPES = [
        (PRIVACY, 'Privacy Notice'),
        (TERMS, 'Terms & Conditions'),
        (ABOUT_TCF, 'About TCF'),
        (CAREERS, 'Careers'),
        (CONTACT_US, 'Contact Us'),
        (MARKETING_ADVERTISEMENT, 'Marketing & Advertisement'),
        (ENGLISH_PROGRAM, 'English Program in Europe'),
        (CHEAPEST_MBA, 'Cheapest MBA'),
        (SUITABLE_PROGRAM_IN_UNI, 'How to find suitable program in University'),
    ]

    name = models.CharField(max_length=255, help_text="Page Name", verbose_name="Name")
    heading = models.CharField(max_length=255, help_text="Page heading", verbose_name="heading")
    content = models.TextField(help_text="content", verbose_name="content")
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class CountryFAQA(TimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.TextField()

    def __str__(self):
        return f"{self.question}"


class TopKeyWords(TimeStampedModel):
    degree_level = models.ForeignKey(DegreeLevel, on_delete=models.CASCADE, blank=True, null=True)
    word = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.word}"


class MarketingCard(TimeStampedModel):
    IMAGE = 'image_card'
    CONTENT = 'content_card'

    CARD_TYPES = [
        (IMAGE, 'Image Card'),
        (CONTENT, 'Content  Card'),
    ]
    card_type = models.CharField(
        max_length=50,
        choices=CARD_TYPES,
        default=CONTENT,
    )
    grid_card_img_front = models.ImageField(upload_to='marketing/images', blank=True, null=True)
    grid_card_img_back = models.ImageField(upload_to='marketing/images', blank=True, null=True)
    list_card_img_front = models.ImageField(upload_to='marketing/images', blank=True, null=True)
    list_card_img_back = models.ImageField(upload_to='marketing/images', blank=True, null=True)
    detail_page_img = models.ImageField(upload_to='marketing/images', blank=True, null=True)
    name = models.CharField(max_length=255, help_text="Card Name", verbose_name="Name")
    heading = models.CharField(max_length=255, help_text="Card heading", verbose_name="heading")
    content = models.TextField(help_text="content", verbose_name="content")
    active = models.BooleanField(default=False)
    priority = models.SmallIntegerField(default=1)


class SeoContent(TimeStampedModel):
    HOME = 'home'
    SCHOLARSHIP = 'scholarship'
    COMPARE = 'compare'
    APPLY = 'apply'
    DISCOVER = 'discover'
    UNIVERSITY_GROUP = 'university-groups'
    CONTACT_US = 'contact-us'
    CAREERS = 'careers'
    ABOUT = 'about'
    MARKETING = 'marketing'
    PRIVACY = 'privacy'
    TERMS_USER = 'terms_and_use'

    CATEGORIES = [
        (HOME, 'Home'),
        (SCHOLARSHIP, 'Scholarship'),
        (COMPARE, 'Course compare'),
        (APPLY, 'Course apply'),
        (DISCOVER, 'Discover'),
        (UNIVERSITY_GROUP, 'University Groups'),
        (CONTACT_US, 'Contact Us'),
        (CAREERS, 'Careers'),
        (ABOUT, 'About'),
        (MARKETING, 'Marketing'),
        (PRIVACY, 'Privacy'),
        (TERMS_USER, 'Terms and Use'),
    ]
    title = models.CharField(max_length=255, help_text="Title", verbose_name="Title")
    category = models.CharField(max_length=50, choices=CATEGORIES, unique=True)
    description = models.TextField()


class AbbreviationElaborationWord(TimeStampedModel):
    elaboration_word = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"{self.elaboration_word}"


class AbbreviationWord(TimeStampedModel):
    abbreviation_word = models.CharField(max_length=7)
    elaboration_words = models.ManyToManyField(AbbreviationElaborationWord)

    def __str__(self):
        return f"{self.abbreviation_word}"


class StopQueryWord(TimeStampedModel):
    stop_word = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"{self.stop_word}"


class ShortUrl(TimeStampedModel):
    uuid = models.CharField(max_length=50, unique=True)
    payload = models.JSONField()

    def __str__(self):
        return f"{self.uuid}"


class PagesDetailsContent(TimeStampedModel):
    CATEGORIES = [
        ('all-groups', 'All Groups'),
        ('all-countries', 'All Countries'),
        ('all-programs', 'All Programs'),
        ('all-scholarships', 'All Scholarships'),
        ('scholarship-country', 'Scholarship Country'),
        ('all-apply-portals', 'All Apply Portals'),
    ]
    title = models.CharField(max_length=255, help_text="Title", verbose_name="Title", blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.category}"
