import pandas as pd
from constructor.utils import (CountryHeader, ParseError, ParseHeaderError)
from constructor import forms
from constructor import models
from constructor.choices import INSTITUTE_TYPES


class ExcelToJsonParser():
    def __init__(self, file, country):
        self.country = country
        self.df = pd.read_excel(file)
        self.df.columns = self.df.columns.str.replace('\n', '')
        self.df = self.df.fillna('None')
        self.header = self.df.columns.ravel()
        self.data = self.df.to_dict(orient='records')
        self.clean_data()

    def clean_data(self):
        for data in self.data:
            for key in data:
                if (data[key] == 'None'):
                    data[key] = None
            if data.get('type'):
                data['type'] = data.get('type').upper()
            if data.get('sector'):
                data['sector'] = data.get('sector').upper()

    def get_header(self):
        default_header = set(CountryHeader().get_header(self.country))
        diffrence = default_header.difference(set(self.header))
        if diffrence:
            return False, ParseHeaderError(list(diffrence), self.country)
        return True, None

    def get_data(self):
        status, diffrence = self.get_header()
        if status:
            row = 2
            for data in self.data:
                country_status, country_response = self.create_or_update_country(data, row)
                if country_status:
                    state_status, state_response = self.create_or_update_state(data, country_response, row)
                    if state_status:
                        city_status, city_response = self.create_or_update_city(data, state_response, row)
                        if city_status:
                            institute_status, institute_response = self.create_or_update_institute(data, city_response,
                                                                                                   row)
                            if institute_status:
                                discipline_status, discipline_response = self.create_or_update_discipline(data, row)
                                if discipline_status:
                                    degree_level_status, degree_level_response = self.create_or_update_degree_level(
                                        data, row)
                                    if degree_level_status:
                                        degree_title_status, degree_title_response = self.create_or_update_degree_title(
                                            data, row)
                                        if degree_title_status:
                                            specialization_status, specialization_response = self.create_or_update_specialization(
                                                data, row)
                                            if specialization_status:
                                                course_status, course_response = self.create_or_update_course(data,
                                                                                                              institute_response,
                                                                                                              discipline_response,
                                                                                                              degree_level_response,
                                                                                                              degree_title_response,
                                                                                                              specialization_response,
                                                                                                              row)
                                                if course_status:
                                                    shedule_status, admission_shedule_response = self.create_or_update_admission_shedule(
                                                        data,
                                                        course_response,
                                                        row)
                                                    if not shedule_status:
                                                        return shedule_status, admission_shedule_response
                                                    fee_status, fee_response = self.create_or_update_fee(data,
                                                                                                         course_response,
                                                                                                         row)
                                                    if not fee_status:
                                                        return fee_status, fee_response
                                                    web_links_status, web_links_response = self.create_or_update_web_links(
                                                        data,
                                                        course_response, row)
                                                    if not web_links_status:
                                                        return web_links_status, web_links_response
                                                    institute_ranking_status, institute_ranking_response = self.create_or_update_institute_ranking(
                                                        data, course_response, row)
                                                    if not institute_ranking_status:
                                                        return institute_ranking_status, web_links_response
                                                    extra_fields_status, extra_fields_response = self.create_or_update_extra_fields(
                                                        data,
                                                        course_response,
                                                        row)
                                                    if not extra_fields_status:
                                                        return extra_fields_status, extra_fields_response
                                                    scholarship_status, scholarship_response = self.create_or_update_scholarship(
                                                        data,
                                                        course_response,
                                                        row)
                                                    if not scholarship_status:
                                                        return scholarship_status, scholarship_response
                                                    pathway_status, pathway_response = self.create_or_update_pathway(
                                                        data,
                                                        course_response,
                                                        row)
                                                    if not pathway_status:
                                                        return pathway_status, pathway_response


                                                else:
                                                    return course_status, course_response
                                            else:
                                                return specialization_status, specialization_response
                                        else:
                                            return degree_title_status, degree_title_response
                                    else:
                                        return degree_level_status, degree_level_response

                                else:
                                    return discipline_status, discipline_response
                            else:
                                return institute_status, institute_response
                        else:
                            return city_status, city_response
                    else:
                        return state_status, state_response
                else:
                    return country_status, country_response
                row = row + 1
            return status, None
        else:
            return status, diffrence

    def create_or_update_country(self, data, row):
        country = forms.CountryForm(data)
        if (country.is_valid()):
            data = country.cleaned_data
            country, status = models.Country.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, country
        else:
            errors = ParseError(country.errors, row)
            return False, errors

    def create_or_update_state(self, data, country, row):
        state_form = forms.StateForm(data, initial={'country': country})
        if (state_form.is_valid()):
            data = state_form.cleaned_data
            state, status = models.State.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, state
        else:
            errors = ParseError(state_form.errors, row)
            return False, errors

    def create_or_update_city(self, data, state, row):
        city_form = forms.CityForm(data, initial={'state': state})
        if (city_form.is_valid()):
            data = city_form.cleaned_data
            city, status = models.City.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, city
        else:
            errors = ParseError(city_form.errors, row)
            return False, errors

    def create_or_update_institute(self, data, city, row):
        institute = forms.InstituteForm(data, initial={'city': city})
        if (institute.is_valid()):
            data = institute.cleaned_data
            institute, status = models.Institute.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, institute
        else:
            errors = ParseError(institute.errors, row)
            return False, errors

    def create_or_update_discipline(self, data, row):
        discipline_form = forms.DisciplineForm(data)
        if (discipline_form.is_valid()):
            data = discipline_form.cleaned_data
            discipline, status = models.Discipline.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, discipline
        else:
            errors = ParseError(discipline_form.errors, row)
            return False, errors

    def create_or_update_degree_level(self, data, row):
        # if data.get('type') == INSTITUTE_TYPES.PATHWAY:
        if not data.get('degree_level'):
            return True, None
        degree_level_form = forms.DegreeLevelForm(data)
        if degree_level_form.is_valid():
            data = degree_level_form.cleaned_data
            degree_level, status = models.DegreeLevel.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, degree_level
        else:
            errors = ParseError(degree_level_form.errors, row)
            return False, errors

    def create_or_update_degree_title(self, data, row):
        if not data.get('degree_title'):
            return True, None
        degree_title_form = forms.DegreeTitleForm(data)
        if degree_title_form.is_valid():
            data = degree_title_form.cleaned_data
            degree_title, status = models.DegreeTitle.objects.update_or_create(name=data.get('name'), defaults=data)
            return True, degree_title
        else:
            errors = ParseError(degree_title_form.errors, row)
            return False, errors

    def create_or_update_specialization(self, data, row):
        specialization_form = forms.SpecializationForm(data)
        if (specialization_form.is_valid()):
            data = specialization_form.cleaned_data
            specialization, status = models.Specialization.objects.update_or_create(name=data.get('name'),
                                                                                    defaults=data)
            return True, specialization
        else:
            errors = ParseError(specialization_form.errors, row)
            return False, errors

    def create_or_update_course(self, data, institute, discipline, degree_level, degree_title, specialization, row):
        course_form = forms.CourseForm(data, initial={'discipline': discipline, 'institute': institute,
                                                      'specializations': specialization, 'degree_title': degree_title,
                                                      'degree_level': degree_level})
        if (course_form.is_valid()):
            data = course_form.cleaned_data
            course, status = models.Course.objects.update_or_create(name=data.get('name'),
                                                                    specializations=data.get('specializations'),
                                                                    degree_title=data.get('degree_title'),
                                                                    discipline=data.get('discipline'), defaults=data)
            return True, course
        else:
            errors = ParseError(course_form.errors, row)
            return False, errors

    def create_or_update_admission_shedule(self, data, course, row):
        shedule_form = forms.AdmissionSheduleForm(data, initial={'course': course})
        if (shedule_form.is_valid()):
            data = shedule_form.cleaned_data
            shedule, status = models.AdmissionShedule.objects.update_or_create(course=data.get('course'), defaults=data)
            return True, shedule
        else:
            errors = ParseError(shedule_form.errors, row)
            return False, errors

    def create_or_update_fee(self, data, course, row):
        fee_form = forms.FeeForm(data, initial={'course': course})
        if (fee_form.is_valid()):
            data = fee_form.cleaned_data
            fee, status = models.Fee.objects.update_or_create(course=data.get('course'), defaults=data)
            return True, fee
        else:
            errors = ParseError(fee_form.errors, row)
            return False, errors

    def create_or_update_web_links(self, data, course, row):
        web_links_form = forms.CourseWebLinkForm(data, initial={'course': course})
        if (web_links_form.is_valid()):
            data = web_links_form.cleaned_data
            web_links, status = models.CourseWebLink.objects.update_or_create(course=data.get('course'), defaults=data)
            return True, web_links
        else:
            errors = ParseError(web_links_form.errors, row)
            return False, errors

    def create_or_update_institute_ranking(self, data, course, row):
        institute_ranking_form = forms.InstituteRankingForm(data, initial={'course': course})
        if (institute_ranking_form.is_valid()):
            data = institute_ranking_form.cleaned_data
            institute_ranking, status = models.InstituteRanking.objects.update_or_create(course=data.get('course'),
                                                                                         defaults=data)
            return True, institute_ranking
        else:
            errors = ParseError(institute_ranking_form.errors, row)
            return False, errors

    def create_or_update_scholarship(self, data, course, row):
        scholarship_form = forms.ScholarshipForm(data, initial={'course': course})
        if (scholarship_form.is_valid()):
            data = scholarship_form.cleaned_data
            scholarship, status = models.Scholarship.objects.update_or_create(course=data.get('course'), defaults=data)
            return True, scholarship
        else:
            errors = ParseError(scholarship_form.errors, row)
            return False, errors

    def create_or_update_pathway(self, data, course, row):
        if (data.get('pathway_entry_requirements')):
            pathway_form = forms.PathwayForm(data, initial={'course': course})
            if (pathway_form.is_valid()):
                data = pathway_form.cleaned_data
                pathway, status = models.Pathway.objects.update_or_create(course=data.get('course'), defaults=data)
                return True, pathway
            else:
                errors = ParseError(pathway_form.errors, row)
                return False, errors
        else:
            return True, None

    def create_or_update_extra_fields(self, data, course, row):
        extra_fields_form = forms.ExtraFieldsForm(data, initial={'course': course})
        if (extra_fields_form.is_valid()):
            data = extra_fields_form.cleaned_data
            extra_fields, status = models.ExtraFields.objects.update_or_create(course=data.get('course'), defaults=data)
            return True, extra_fields
        else:
            errors = ParseError(extra_fields_form.errors, row)
            return False, errors
