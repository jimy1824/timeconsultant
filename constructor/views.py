import os
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import redirect
from django.views.generic import TemplateView
from celery_progress.backend import Progress
from .forms import UploadExcelForm, ImportScholarshipForm, ImportFileForm, CourseDeleteForm
from .helper.import_course_data import CourseExcelToJsonParser
from .helper.import_data import ExcelToJsonParser
from .helper.import_scholarships_data import ScholarshipExcelToJsonParser
from .models import Course
from .tasks import import_scholarship_task
from .tasks.import_course_task import import_course_task
from .utils import in_memory_file_to_temp
from .tasks.import_institutes_logos_task import import_institutes_logo_task
from .tasks.import_institutes_raking_task import import_institutes_raking_task
from .tasks.import_institutes_panels_tasks import import_institutes_panels_task
from django.contrib import messages


class UploadExcelData(View):
    form_class = UploadExcelForm
    initial = {'key': 'value'}
    template_name = 'data_upload_form.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            status, errors = CourseExcelToJsonParser(request.FILES['file']).get_data()
            if not status:
                return render(request, self.template_name, {'form': form, 'errors': errors})
            return redirect('home')
        return render(request, self.template_name, {'form': form})


class ImportScholarships(View):
    form_class = ImportScholarshipForm
    template_name = 'import_scholarships.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            status, errors = ScholarshipExcelToJsonParser(request.FILES['file']).get_data()
            if not status:
                return render(request, self.template_name, {'form': form, 'errors': errors})
            return redirect('home')
        return render(request, self.template_name, {'form': form})


class IndexTemplateView(TemplateView):
    template_name = "data_upload_form.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


@login_required
def import_courses_view(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_course_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


class ScholarShipImportView(TemplateView):
    template_name = "scholarship_import_form.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


# @method_decorator(login_required)
@login_required
def import_scholarship_view(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_scholarship_task.import_scholarship_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


class InstitutesLogoImportView(TemplateView):
    template_name = "import_institute_logo_form.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


@login_required()
def import_institute_logos_view(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_institutes_logo_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


class CourseDeleteView(View):
    template_name = 'delete_course.html'
    form_class = CourseDeleteForm

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            country = form.cleaned_data.get('country')
            courses = Course.objects.filter(campus__city__state__country=country)
            courses.delete()
            msg = 'Successfully Deleted ' + str(courses.count()) + ' course against ' + country.name
            messages.success(request, msg)
            return redirect('home')
        return render(request, self.template_name,
                      {'form': form})


class InstitutesRankingImportView(TemplateView):
    template_name = "import_institutes_ranking_form.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


@login_required()
def import_institute_ranking_view(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_institutes_raking_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


class InstitutesPanelImportView(TemplateView):
    template_name = "import_institute_panel_form.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


@login_required()
def import_institute_panel_view(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_institutes_panels_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404


@login_required()
def import_specialization_files(request):
    """
        The column of the excel file should be part of
        headers
        """
    form = ImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        filepath = os.path.join(
            settings.MEDIA_ROOT, in_memory_file_to_temp(form.cleaned_data.get('document_file'))
        )
        task = import_institutes_panels_task.delay(os.path.join(settings.MEDIA_ROOT, filepath))
        return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
    raise Http404
