import math
from django import forms
from constructor.choices import COUNTRY
from constructor.models import (Country, State, City, Institute, Course, Discipline, Specialization, DegreeLevel,
                                CourseTitle, CourseFee, InstituteRanking,
                                Scholarship, InstituteGroup, Currency, CourseDuration, PathwayGroup, CourseApply,
                                CourseExam, CourseIntakeAndDeadLine, ScholarshipStartDate, ScholarshipCloseDate,
                                InstituteCampus, ApplyPortal)
from .choices import (INSTITUTE_TYPES, SECTOR, INSTITUTE_PANEL, DECISION)
from django.utils.translation import gettext_lazy as _
from constructor.helper import headers
from common.helper.map import Map


class UploadExcelForm(forms.Form):
    file = forms.FileField()


class ImportFileForm(forms.Form):
    document_file = forms.FileField()


class ImportScholarshipForm(forms.Form):
    file = forms.FileField(label='upload scholarship data file',
                           widget=forms.FileInput(attrs={'class': 'form-control'}))


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = "__all__"
        error_messages = {
            'name': {
                'required': _("Country Name is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0])
        super().__init__(*args, **kwargs)

    def clean_data(self, data):
        if data.get(headers.COUNTRY) is not None:
            data = {'name': data.get(headers.COUNTRY).strip().lower(), 'order': 1}
        return tuple([data])


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = "__all__"
        error_messages = {
            'name': {
                'required': _("State Name is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        params = {'name': data.get(headers.STATE), headers.COUNTRY: initial.get(headers.COUNTRY)}
        return tuple([params])


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = "__all__"
        error_messages = {
            'name': {
                'required': _("City Name is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        params = {'name': data.get(headers.CITY), headers.POSTEL_CODE: data.get(headers.POSTEL_CODE),
                  headers.STATE: initial.get(headers.STATE)}
        return tuple([params])


class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = "__all__"
        error_messages = {
            'institute_name': {
                'required': _("Institute Name is required field."),
            },
            'type': {
                'invalid_choice': _(
                    " Institute type is Invalid choice,Types may be UNIVERSITY,COLLEGE,TAFE,PATHWAY_COLLEGE,"
                    "PATHWAY_UNIVERSITY."),
                'required': _("institute Type is required ,Types may be UNIVERSITY,COLLEGE,TAFE,PATHWAY_COLLEGE,"
                              "PATHWAY_UNIVERSITY."),
            },
            'sector': {
                'invalid_choice': _(" Invalid choice,Sector may be  PUBLIC or PRIVATE."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = InstituteForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
            if field == headers.INSTITUTE_SECTOR and data.get(headers.INSTITUTE_SECTOR) is not None:
                params[field] = data.get(headers.INSTITUTE_SECTOR)
            if field == headers.INSTITUTE_GROUP and data.get(headers.INSTITUTE_GROUP) is not None:
                params[field] = InstituteGroup.objects.filter(key=data.get(headers.INSTITUTE_GROUP)).first()
            if field == headers.INSTITUTE_PANEL and data.get(headers.INSTITUTE_PANEL) is None:
                params[field] = INSTITUTE_PANEL.p3
            if field == headers.COMMONAPP_UNIVERSITY and data.get(headers.COMMONAPP_UNIVERSITY) is None:
                params[field] = DECISION.tbc
            if field == headers.ESSAY_REQUIREMENT and data.get(headers.ESSAY_REQUIREMENT) is None:
                params[field] = DECISION.tbc
            if field == headers.INSTITUTE_SCHOLARSHIP_SEPARATE_APPLICATION_REQUIRED and data.get(
                    headers.INSTITUTE_SCHOLARSHIP_SEPARATE_APPLICATION_REQUIRED) is None:
                params[field] = DECISION.tbc
            if field == headers.INSTITUTE_ACCOMMODATION_AVAILABILITY and data.get(
                    headers.INSTITUTE_ACCOMMODATION_AVAILABILITY) is None:
                params[field] = DECISION.tbc
            if field == headers.INSTITUTE_PATHWAY_GROUP and data.get(headers.INSTITUTE_PATHWAY_GROUP) is not None:
                params[field] = PathwayGroup.objects.filter(key=data.get(headers.INSTITUTE_PATHWAY_GROUP)).first()
            if field == headers.APPLY_PORTAL and data.get(headers.APPLY_PORTAL) is not None:
                params[field] = ApplyPortal.objects.filter(key=data.get(headers.APPLY_PORTAL)).first()

        # if not (params.keys() >= {headers.LAT, headers.Lng}) and (
        #         params.keys() >= {headers.ADDRESS, headers.INSTITUTE_NAME}):
        #     map = Map()
        #     address = params[headers.INSTITUTE_NAME] + ' ' + params[headers.ADDRESS]
        #     lat, lng = map.get_coordinates(address)
        #     if lat and lng:
        #         params[headers.LAT] = lat
        #         params[headers.Lng] = lng
        # params[headers.CITY] = initial.get(headers.CITY)
        return tuple([params])


class InstituteCampusForm(forms.ModelForm):
    class Meta:
        model = InstituteCampus
        fields = "__all__"
        error_messages = {
            'campus': {
                'required': _("Institute Campus Name is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = InstituteCampusForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        if not (params.keys() >= {headers.LAT, headers.Lng}) and (
                params.keys() >= {headers.ADDRESS}):
            map = Map()
            institute = initial.get('institute')
            address = institute.institute_name + ' ' + params[headers.ADDRESS]
            lat, lng = map.get_coordinates(address)
            print('lat', lat, 'lng', lng)
            if lat and lng:
                params[headers.LAT] = lat
                params[headers.Lng] = lng
        params[headers.CITY] = initial.get(headers.CITY)
        params['institute'] = initial.get('institute')
        return tuple([params])


# class DisciplineForm(forms.ModelForm):
#     class Meta:
#         model = Discipline
#         fields = "__all__"
#         error_messages = {
#             'name': {
#                 'required': _("Discipline Name is required field."),
#             },
#         }
#
#     def __init__(self, *args, **kwargs):
#         args = self.clean_data(args[0])
#         super().__init__(*args, **kwargs)
#
#     def clean_data(self, data):
#         data = {'name': data.get(headers.DISCIPLINE)}
#         return tuple([data])


# class DegreeLevelForm(forms.ModelForm):
#     class Meta:
#         model = DegreeLevel
#         fields = "__all__"
#         error_messages = {
#             'name': {
#                 'required': _("Degree Level is required field."),
#             },
#         }
#
#     def __init__(self, *args, **kwargs):
#         args = self.clean_data(args[0])
#         super().__init__(*args, **kwargs)
#
#     def clean_data(self, data):
#         data = {'name': data.get(headers.DEGREE_LEVEL)}
#         return tuple([data])


# class DegreeTitleForm(forms.ModelForm):
#     class Meta:
#         model = CourseTitle
#         fields = "__all__"
#         error_messages = {
#             'name': {
#                 'required': _("Degree Title is required field."),
#             },
#         }
#
#     def __init__(self, *args, **kwargs):
#         args = self.clean_data(args[0])
#         super().__init__(*args, **kwargs)
#
#     def clean_data(self, data):
#         data = {'name': data.get(headers.DEGREE_TITLE)}
#         return tuple([data])


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = "__all__"
        error_messages = {
            'name': {
                'required': _("Specialization is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0])
        super().__init__(*args, **kwargs)

    def clean_data(self, data):
        data = {'name': data.get(headers.COURSE_SPECIALIZATION)}
        return tuple([data])


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = "__all__"
        error_messages = {
            'name': {
                'required': _("Course Name is required field."),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = CourseForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
            if field == headers.COURSE_LANGUAGE and data.get(headers.COURSE_LANGUAGE) is None:
                params[field] = 'English'
            if field == 'name' and data.get(headers.COURSE_NAME) is not None:
                params[field] = data.get(headers.COURSE_NAME)
            if field == 'entry' and data.get(headers.PATHWAY_OR_DIRECT_ENTRY) is not None:
                params[field] = data.get(headers.PATHWAY_OR_DIRECT_ENTRY)
        params['campus'] = initial.get('campus')
        params['discipline'] = initial.get(headers.DISCIPLINE)
        params['degree_level'] = initial.get(headers.DEGREE_LEVEL)
        params['course_title'] = initial.get(headers.COURSE_TITLE)
        params['specialization'] = initial.get(headers.COURSE_SPECIALIZATION)
        params['base_fee'] = 0
        return tuple([params])


class CourseDurationForm(forms.ModelForm):
    class Meta:
        model = CourseDuration
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = CourseDurationForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        return tuple([params])


class CourseIntakeAndDeadLineForm(forms.ModelForm):
    class Meta:
        model = CourseIntakeAndDeadLine
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = CourseIntakeAndDeadLineForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        return tuple([params])


class FeeForm(forms.ModelForm):
    class Meta:
        model = CourseFee
        fields = "__all__"
        error_messages = {
            'value': {
                'invalid': _("Course Fee must be number field. character is given"),
            },
        }

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = FeeForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        params['currency'] = initial.get('currency')
        return tuple([params])


class CourseWebLinkForm(forms.ModelForm):
    class Meta:
        model = CourseApply
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = CourseWebLinkForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        if params['url']:
            params['url'] = params['url'].replace(' ', '')
        return tuple([params])


class InstituteRankingForm(forms.ModelForm):
    class Meta:
        model = InstituteRanking
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = InstituteRankingForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['institute'] = initial.get('institute')
        return tuple([params])


class InstituteRankingImportForm(forms.ModelForm):
    class Meta:
        model = InstituteRanking
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        return tuple([initial])


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = ScholarshipForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        return tuple([params])


class CourseExamForm(forms.ModelForm):
    class Meta:
        model = CourseExam
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = CourseExamForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['course'] = initial.get('course')
        return tuple([params])


class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = ScholarshipForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['institute'] = initial.get('institute')
        params['scholarship_type'] = initial.get('scholarship_type')
        params['discipline'] = initial.get('discipline')
        params['degree_level'] = initial.get('degree_level')
        params['institute_name_organizational_scholarship'] = initial.get('institute_name_organizational_scholarship')
        return tuple([params])


class ScholarshipStartDateForm(forms.ModelForm):
    class Meta:
        model = ScholarshipStartDate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = ScholarshipStartDateForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['scholarship'] = initial.get('scholarship')
        return tuple([params])


class ScholarshipCloseDateForm(forms.ModelForm):
    class Meta:
        model = ScholarshipCloseDate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        args = self.clean_data(args[0], kwargs.get('initial'))
        super().__init__(*args, **kwargs)

    def clean_data(self, data, initial):
        fields = ScholarshipCloseDateForm.base_fields.keys()
        params = {}
        for field in fields:
            if data.get(field) is not None:
                params[field] = data.get(field)
        params['scholarship'] = initial.get('scholarship')
        return tuple([params])


class CourseDeleteForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all().order_by('name'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].label = "Name"
        self.fields['country'].widget.attrs.update({'class': 'form-control greyInput'})
