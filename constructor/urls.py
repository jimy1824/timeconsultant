from django.urls import path
from constructor import views

urlpatterns = [

    # path('upload-excel-data', views.UploadExcelData.as_view(), name='upload-excel-data'),
    path('import_data/', views.IndexTemplateView.as_view(), name='import_data'),
    path('import-courses', views.import_courses_view, name='import-courses'),
    path('import-institute-logos', views.import_institute_logos_view, name='import-institute-logos'),
    # path('import-scholarships', views.ImportScholarships.as_view(), name='import-scholarships'),
    path('import-scholarships/', views.ScholarShipImportView.as_view(), name='import_scholarships'),
    path('import-scholarships-data', views.import_scholarship_view, name='import_scholarships_data'),
    path('import-institute-logos-data', views.InstitutesLogoImportView.as_view(), name='import-institute-logos-data'),

    path('import-institute-raking', views.InstitutesRankingImportView.as_view(), name='import-institute-raking'),
    path('import-institute-raking-data', views.import_institute_ranking_view, name='import-institute-raking-data'),

    path('import-institute-panels', views.InstitutesPanelImportView.as_view(), name='import-institute-panels'),
    path('import-institute-panels-data', views.import_institute_panel_view, name='import-institute-panels-data'),

    path('delete_courses/', views.CourseDeleteView.as_view(), name='delete_course'),

    path('get_specialization/', views.import_specialization_files, name='get_specialization'),

]
