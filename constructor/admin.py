from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from constructor import models as ConstructorModels
from import_export.admin import ImportExportModelAdmin, ImportMixin, ExportMixin
from constructor import resources
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.admin import SimpleListFilter
from admin_auto_filters.filters import AutocompleteFilter
from django_summernote.admin import SummernoteModelAdmin
from django import forms
# filters
from django.contrib.auth.admin import UserAdmin


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = ConstructorModels.CustomUser
        fields = '__all__'

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        if len(self.cleaned_data["password"]) < 16:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


@admin.register(ConstructorModels.CustomUser)
class CustomUserAdmin(ImportExportModelAdmin):
    form = UserCreationForm
    list_display = [field.name for field in ConstructorModels.CustomUser._meta.fields]
    ordering = ['id']
    search_fields = ['id', 'email']


class InstituteCampusFilter(AutocompleteFilter):
    title = 'Institute Campus Name'
    field_name = 'campus'


class DisciplineFilter(AutocompleteFilter):
    title = 'Discipline'
    field_name = 'discipline'


class DegreeLevelFilter(AutocompleteFilter):
    title = 'Degree level'
    field_name = 'degree_level'


class SpecializationFilter(AutocompleteFilter):
    title = 'specialization Name'  # display title
    field_name = 'specialization'  # name of the foreign key field


# custom filters

class StateCustomFilter(SimpleListFilter):
    title = 'State'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        if 'campus__city__state__country__name' in request.GET:
            country = request.GET['campus__city__state__country__name']
            state = set([i for i in
                         ConstructorModels.State.objects.filter(country__name=country).order_by(
                             'name').distinct('name')])
            # else:
            #     state = set([s for s in ConstructorModels.State.objects.all()])
            return [(i.id, i.name) for i in state]
        return []

    def queryset(self, request, queryset):
        return queryset


class CityCustomFilter(SimpleListFilter):
    title = 'City'
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        if 'state' in request.GET:
            state_id = request.GET['state']
            city = set(
                [i for i in
                 ConstructorModels.City.objects.filter(state__id=state_id).order_by('name').distinct('name')])
            return [(i.id, i.name) for i in city]
        return []

    def queryset(self, request, queryset):
        return queryset


class InstituteCustomFilter(SimpleListFilter):
    title = 'Institute'
    parameter_name = 'institute'

    def lookups(self, request, model_admin):
        if 'city' in request.GET:
            city_id = request.GET['city']
            institutes = set([i for i in
                              ConstructorModels.Institute.objects.filter(institutecampus__city__id=city_id).order_by(
                                  'institute_name')])
            return [(i.id, i.institute_name) for i in institutes]
        elif 'state' in request.GET:
            state_id = request.GET['state']
            institutes = set([i for i in
                              ConstructorModels.Institute.objects.filter(
                                  institutecampus__city__state__id=state_id).order_by(
                                  'institute_name')])
            return [(i.id, i.institute_name) for i in institutes]

        elif 'campus__city__state__country__name' in request.GET:
            country = request.GET['campus__city__state__country__name']
            institutes = set([i for i in
                              ConstructorModels.Institute.objects.filter(
                                  institutecampus__city__state__country__name=country).order_by(
                                  'institute_name')])
            return [(i.id, i.institute_name) for i in institutes]
        return []

    def queryset(self, request, queryset):
        if 'campus' in request.GET:
            campus_id = request.GET['campus']
            if 'discipline' in request.GET:
                discipline_id = request.GET['discipline']
                queryset = queryset.filter(discipline__id=discipline_id)
            if 'degree_level' in request.GET:
                degree_level_id = request.GET['degree_level']
                queryset = queryset.filter(degree_level__id=degree_level_id)
            queryset = queryset.filter(campus__id=campus_id)
        elif 'institute' in request.GET:
            institute_id = request.GET['institute']
            return queryset.filter(campus__institute__id=institute_id)
        elif 'city' in request.GET:
            city_id = request.GET['city']
            return queryset.filter(campus__city__id=city_id)
        elif 'state' in request.GET:
            state_id = request.GET['state']
            return queryset.filter(campus__city__state__id=state_id)
        elif 'institute__city__state__country__name' in request.GET:
            country_name = request.GET['institute__city__state__country__name']
            return queryset.filter(campus__city__state__country__name=country_name)
        return queryset


class InstituteCampusCustomFilter(SimpleListFilter):
    title = 'Campus'
    parameter_name = 'campus'

    def lookups(self, request, model_admin):
        if 'institute' in request.GET:
            institute_id = request.GET['institute']
            campus = set(
                [i for i in
                 ConstructorModels.InstituteCampus.objects.filter(institute__id=institute_id).order_by('campus')])
            return [(i.id, i.campus) for i in campus]
        return []

    def queryset(self, request, queryset):
        return queryset


class DisciplineCustomFilter(SimpleListFilter):
    title = 'Discipline'
    parameter_name = 'discipline'

    def lookups(self, request, model_admin):
        if 'campus' in request.GET:
            campus_id = request.GET['campus']
            disciplines = ConstructorModels.InstituteCampus.objects.filter(id=campus_id).values_list(
                'course__discipline_id', flat=True)
            disciplines = set(
                [i for i in
                 ConstructorModels.Discipline.objects.filter(id__in=disciplines).order_by('name')])
            return [(d.id, d.name) for d in disciplines]
        return []

    def queryset(self, request, queryset):
        return queryset


class DegreeLevelCustomFilter(SimpleListFilter):
    title = 'Degree level'
    parameter_name = 'degree_level'

    def lookups(self, request, model_admin):
        if 'campus' in request.GET and 'discipline' in request.GET:
            campus_id = request.GET['campus']
            discipline_id = request.GET['discipline']
            degree_levels = ConstructorModels.InstituteCampus.objects.filter(id=campus_id,
                                                                             course__discipline__id=discipline_id).values_list(
                'course__degree_level__id', flat=True)
            degree_levels = set(
                [i for i in
                 ConstructorModels.DegreeLevel.objects.filter(id__in=degree_levels).order_by('display_name')])
            return [(d.id, d.display_name) for d in degree_levels]
        return []

    def queryset(self, request, queryset):
        return queryset


# Register your models here.


class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(ConstructorModels.Currency)
class CurrencyAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.Currency._meta.fields]
    ordering = ['id']


@admin.register(ConstructorModels.Region)
class RegionAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.Region._meta.fields]
    ordering = ['id']
    search_fields = ['name', ]


@admin.register(ConstructorModels.Country)
class CountryAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ['id', 'name', 'region', 'order', 'country_logo', 'country_icon']
    ordering = ['id']
    search_fields = ['id', 'name']
    list_display_links = ('name',)
    list_filter = ['region__name', ]
    autocomplete_fields = ["region"]

    def country_logo(self, obj):
        return format_html('<img src="{}" width="100" height="100" />'.format(obj.logo))

    def country_icon(self, obj):
        return format_html('<img src="{}" width="100" height="100" />'.format(obj.icon))


@admin.register(ConstructorModels.State)
class StateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.State._meta.fields]
    ordering = ['id']
    search_fields = ['id', 'name', 'country__name']
    list_filter = ['country__name']
    autocomplete_fields = ["country"]


@admin.register(ConstructorModels.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'state', 'updated_at']
    ordering = ['id']
    search_fields = ['id', 'name', 'state__name']
    list_filter = ['state__country__name', 'state__name']
    list_display_links = ('name',)
    autocomplete_fields = ["state"]


@admin.register(ConstructorModels.InstituteGroup)
class InstituteGroupAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['logo_tag', 'id', 'display_name', 'updated_at']
    ordering = ['id']
    search_fields = ('display_name', 'key')
    list_display_links = ['id']

    def logo_tag(self, obj):
        return format_html('<img src="{}" width="150" height="150" />'.format(obj.logo))


@admin.register(ConstructorModels.InstituteRanking)
class InstituteRankingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.InstituteRanking._meta.fields]
    ordering = ['id']
    search_fields = ('ranking_type', 'value')
    raw_id_fields = ["institute", ]
    list_filter = (
        ('institute__institutecampus__city__state__country__name', DropdownFilter),
    )


@admin.register(ConstructorModels.PathwayGroup)
class PathwayGroupAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ['logo_tag', 'id', 'display_name', 'updated_at']
    ordering = ['id']
    list_display_links = ['id']
    search_fields = ('display_name', 'key')

    def logo_tag(self, obj):
        return format_html('<img src="{}" width="150" height="150" />'.format(obj.logo))


@admin.register(ConstructorModels.ApplyPortal)
class ApplyPortalAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ['id', 'display_name', 'key', 'order', 'logo_tag']
    ordering = ['id']
    list_display_links = ['display_name']
    search_fields = ('display_name', 'key')

    def logo_tag(self, obj):
        return format_html('<img src="{}" width="150" height="150" />'.format(obj.logo))


class InstituteCampusInline(admin.TabularInline):
    model = ConstructorModels.InstituteCampus
    extra = 0


class LogoFilter(SimpleListFilter):
    title = 'logo'  # or use _('country') for translated title
    parameter_name = 'logo'

    def lookups(self, request, model_admin):
        return [('with-logo', 'without-logo')]

    def queryset(self, request, queryset):
        if self.value() == 'without-logo':
            return queryset.filter(logo__isnull=True)
        if self.value() == 'with-logo':
            return queryset.filter(logo__isnull=False)
        if self.value():
            return queryset.filter()


@admin.register(ConstructorModels.Institute)
class InstituteAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('institute_description',)
    resource_class = resources.InstituteResource
    list_display = ['id', 'institute_name', 'show_campus', 'logo_tag']
    ordering = ['id']
    search_fields = ('institute_name',)
    inlines = (
        InstituteCampusInline,
    )
    list_display_links = ['id', 'institute_name']
    list_filter = (
        ('institutecampus__city__state__country__name', DropdownFilter),
    )

    def logo_tag(self, obj):
        return format_html('<img src="{}" width="150" height="150" />'.format(obj.logo))

    def show_campus(self, obj):
        return "\n".join([a.campus + " , " for a in obj.institutecampus_set.all()])


@admin.register(ConstructorModels.InstituteCampus)
class InstituteCampusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    # resource_class = resources.InstituteResource
    # list_display = [field.name for field in ConstructorModels.InstituteCampus._meta.fields]
    list_display = ['id', 'institute', 'campus', 'city', '_state',
                    '_country', 'latitude', 'longitude', 'address']
    ordering = ['id']
    search_fields = ('id', 'campus', 'institute__institute_name')
    autocomplete_fields = ["city", "institute"]

    def _state(self, obj):
        return obj.city.state.name

    def _country(self, obj):
        return obj.city.state.country.name


@admin.register(ConstructorModels.Discipline)
class DisciplineAdmin(ImportExportModelAdmin, SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = [field.name for field in ConstructorModels.Discipline._meta.fields]
    ordering = ['id']
    search_fields = ('name', 'key')


@admin.register(ConstructorModels.SubDiscipline)
class SubDisciplineAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.SubDiscipline._meta.fields]
    ordering = ['id']
    search_fields = ('name', 'key')


@admin.register(ConstructorModels.Specialization)
class SpecializationAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.Specialization._meta.fields]
    ordering = ['id']
    search_fields = ('name',)


@admin.register(ConstructorModels.DegreeLevel)
class DegreeLevelAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.DegreeLevel._meta.fields]
    ordering = ['id']
    search_fields = ('display_name', 'key')


@admin.register(ConstructorModels.CourseTitle)
class CourseTitleAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.CourseTitle._meta.fields]
    ordering = ['id']
    search_fields = ('display_name', 'key')


class CourseDurationInline(admin.TabularInline):
    model = ConstructorModels.CourseDuration
    extra = 0


class CourseIntakeAndDeadLineInline(admin.TabularInline):
    model = ConstructorModels.CourseIntakeAndDeadLine
    extra = 0


class CourseFeeInline(admin.TabularInline):
    model = ConstructorModels.CourseFee
    extra = 0


class CourseExamInline(admin.TabularInline):
    model = ConstructorModels.CourseExam
    extra = 0


class CourseApplyInline(admin.TabularInline):
    model = ConstructorModels.CourseApply
    extra = 0


@admin.register(ConstructorModels.Course)
class CourseAdmin(SummernoteModelAdmin, ImportMixin, admin.ModelAdmin):
    # resource_class = resources.CourseResource
    summernote_fields = ('overview', 'structure', 'career_prospects')
    list_display = (
        "id", "name", "campus", 'get_institute', "get_country", 'get_state', "get_city",
        "specialization", "discipline",
        "degree_level",
        "course_title",
        "duration", "base_fee")
    ordering = ['id']
    search_fields = ['id', 'name', 'campus__institute__institute_name', 'campus__city__state__country__name']
    # list_filter = ['institute__city__state__country' ]
    autocomplete_list_filter = ('discipline', 'specialization',)
    list_filter = (
        ('campus__city__state__country__name', DropdownFilter),
        # relative filters
        StateCustomFilter,
        CityCustomFilter,
        InstituteCustomFilter,
        InstituteCampusCustomFilter,
        DisciplineCustomFilter,
        DegreeLevelCustomFilter,
        # autocomplete filters
        DegreeLevelFilter,
        DisciplineFilter,
        InstituteCampusFilter,
        SpecializationFilter,

    )
    autocomplete_fields = ["discipline", "specialization", "course_title", "degree_level", "campus"]

    inlines = (
        CourseDurationInline,
        CourseIntakeAndDeadLineInline,
        CourseFeeInline,
        CourseExamInline,
        CourseApplyInline,
    )

    def get_country(self, obj):
        return obj.campus.city.state.country

    def get_state(self, obj):
        return obj.campus.city.state.name

    def get_city(self, obj):
        return obj.campus.city.name

    def get_institute(self, obj):
        return obj.campus.institute.institute_name

    def duration(self, obj):
        return "\n".join([str(p.duration_one) for p in obj.courseduration_set.all()])


@admin.register(ConstructorModels.CourseDuration)
class CourseDurationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.CourseDuration._meta.fields]
    ordering = ['id']
    raw_id_fields = ('course',)


@admin.register(ConstructorModels.CourseIntakeAndDeadLine)
class CourseIntakeAndDeadLineAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.CourseIntakeAndDeadLine._meta.fields]
    ordering = ['id']
    raw_id_fields = ('course',)


@admin.register(ConstructorModels.CourseFee)
class CourseFeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.CourseFee._meta.fields]
    ordering = ['id']
    raw_id_fields = ('course',)
    search_fields = ['course__id']
    list_filter = ('type',)


@admin.register(ConstructorModels.CourseApply)
class CourseApplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'course']
    ordering = ['id']
    search_fields = ['id', 'type']
    list_display_links = ('type',)
    raw_id_fields = ('course',)


@admin.register(ConstructorModels.CourseExam)
class CourseExamAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.CourseExam._meta.fields]
    ordering = ['id']
    raw_id_fields = ('course',)


@admin.register(ConstructorModels.ScholarshipType)
class ScholarshipTypeAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ConstructorModels.ScholarshipType._meta.fields]
    ordering = ['id']
    search_fields = ['id', 'key']


class ScholarshipTypeInline(admin.TabularInline):
    model = ConstructorModels.Scholarship.scholarship_type.through
    extra = 0


class DisciplineInline(admin.TabularInline):
    model = ConstructorModels.Scholarship.discipline.through
    extra = 0


class DegreeLevelInline(admin.TabularInline):
    model = ConstructorModels.Scholarship.degree_level.through
    extra = 0


class ScholarshipStartDateInline(admin.TabularInline):
    model = ConstructorModels.ScholarshipStartDate
    extra = 0


class ScholarshipCloseDateInline(admin.TabularInline):
    model = ConstructorModels.ScholarshipCloseDate
    extra = 0


@admin.register(ConstructorModels.Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['id', 'scholarship_name', 'institute']
    ordering = ['id']
    exclude = ('scholarship_type', 'degree_level', 'discipline')
    raw_id_fields = ('institute', 'institute_name_organizational_scholarship')
    search_fields = ['scholarship_name', 'institute__institute_name']
    list_filter = (
        ('institute__institutecampus__city__state__country__name', DropdownFilter),
    )
    inlines = (
        ScholarshipTypeInline,
        DegreeLevelInline,
        DisciplineInline,
        ScholarshipStartDateInline,
        ScholarshipCloseDateInline
    )


@admin.register(ConstructorModels.ScholarshipStartDate)
class ScholarshipStartDateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.ScholarshipStartDate._meta.fields]
    ordering = ['id']
    raw_id_fields = ["scholarship"]


@admin.register(ConstructorModels.ScholarshipCloseDate)
class ScholarshipCloseDateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.ScholarshipCloseDate._meta.fields]
    ordering = ['id']
    raw_id_fields = ["scholarship"]


@admin.register(ConstructorModels.ScholarshipOrganization)
class ScholarshipOrganizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConstructorModels.ScholarshipOrganization._meta.fields]
    ordering = ['id']
    autocomplete_fields = ["country"]


@admin.register(ConstructorModels.Blog)
class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['id', 'heading', 'created_at', 'updated_at']
    ordering = ['id']
    list_display_links = ('heading',)


@admin.register(ConstructorModels.DynamicPages)
class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['id', 'name', 'heading']
    list_display_links = ('name',)
    ordering = ['updated_at']


@admin.register(ConstructorModels.CountryFAQA)
class FAQAAdmin(ImportExportModelAdmin):
    autocomplete_fields = ["country"]
    list_display = ['id', 'country', 'question']
    list_display_links = ('question',)
    ordering = ['updated_at']


@admin.register(ConstructorModels.TopKeyWords)
class TopKeyWordsAdmin(admin.ModelAdmin):
    list_display = ['id', 'word', 'degree_level']
    autocomplete_fields = ["degree_level"]
    list_filter = ('degree_level',)
    ordering = ['updated_at']


@admin.register(ConstructorModels.MarketingCard)
class MarketingCardAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['id', 'name', 'priority', 'active', 'updated_at', 'created_at']
    ordering = ['updated_at']


@admin.register(ConstructorModels.SeoContent)
class SeoContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'updated_at', 'created_at']
    ordering = ['updated_at']
    search_fields = ['title', 'category']


@admin.register(ConstructorModels.AbbreviationElaborationWord)
class AbbreviationElaborationWordAdmin(admin.ModelAdmin):
    list_display = ['id', 'elaboration_word']
    ordering = ['updated_at']
    search_fields = ['elaboration_word', ]


@admin.register(ConstructorModels.AbbreviationWord)
class AbbreviationWordAdmin(admin.ModelAdmin):
    list_display = ['id', 'abbreviation_word']
    ordering = ['updated_at']
    search_fields = ['abbreviation_word', ]
    filter_horizontal = (
        'elaboration_words',
    )


@admin.register(ConstructorModels.StopQueryWord)
class StopQueryWordAdmin(admin.ModelAdmin):
    list_display = ['id', 'stop_word']
    ordering = ['updated_at']
    search_fields = ['stop_word', ]
    # formfield_overrides = {
    #     # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
    #     # 'words_list': {'widget': JSONEditorWidget},
    #     models.JSONField: {'widget': JSONEditorWidget},
    # }


from django.db import models


@admin.register(ConstructorModels.ShortUrl)
class ShortUrlAdmin(admin.ModelAdmin):
    list_display = ['id', 'uuid']
    ordering = ['updated_at']
    search_fields = ['uuid', ]
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ConstructorModels.PagesDetailsContent)
class PagesDetailsContentAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ['id', 'title', 'category', 'description']
    list_display_links = ('category',)
    ordering = ['updated_at']
