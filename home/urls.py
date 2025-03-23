from django.conf.urls import url
from home import views
from home.views import course_autocomplete
from django.urls import path, include
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('search-results', views.InstitutesView.as_view(), name='search-results'),
    url(r'^api/course-autocomplete/', course_autocomplete, name='course-autocomplete'),

]