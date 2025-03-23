from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from api import views
from api.allviews.country import CountryView, StateViewSet, CityViewSet
from api.allviews.dynamic_pages import DynamicPagesView
from api.allviews.institute import InstituteViewSet, CampusViewSet
from api.allviews.course import CourseViewSet
from api.allviews.pathway_groups import PathwayGroupView, InstituteGroupView, ApplyPortalView
from api.allviews.scholarship import ScholarshipView, ScholarshipTypeView, ScholarshipCountryView
from api.allviews.blog import BlogView
from api.allviews import auto_complete
from api.allviews.serach_nested_course import SearchNestedCourseView
from api.allviews.regions import RegionViewSet
from api.allviews.top_words import TopWordsViewSet
from api.allviews.currency import CurrencyView
from api.allviews.marketing import MarketingCardView
from api.allviews.short_url_parser import ShortUrlView
from api.allviews.payments import JazzCashPayment
from .allviews.page_details import PagesDetailViewSet

router = routers.DefaultRouter()
router.register(r'country', CountryView)
router.register(r'state', StateViewSet)
router.register(r'city', CityViewSet)
router.register(r'discipline', views.DisciplineViewSet)
router.register(r'degree_level', views.DegreeLevelViewSet)
router.register(r'course_title', views.CourseTitleViewSet)
router.register(r'institute', InstituteViewSet)
router.register(r'pathway-group', PathwayGroupView)
router.register(r'institute-group', InstituteGroupView)
router.register(r'apply-portal', ApplyPortalView)
router.register(r'campus', CampusViewSet)
router.register(r'course', CourseViewSet)
router.register(r'scholarship-type', ScholarshipTypeView)
router.register(r'scholarship', ScholarshipView)
router.register(r'blog', BlogView)
router.register(r'pages', DynamicPagesView)
router.register(r'search-course', SearchNestedCourseView)
router.register(r'regions', RegionViewSet)
router.register(r'top-words', TopWordsViewSet)
router.register(r'currency', CurrencyView)
router.register(r'marketing-card', MarketingCardView)
router.register(r'short-url', ShortUrlView)
router.register(r'page', PagesDetailViewSet)
# router.register(r'course-auto-suggestion/', )

urlpatterns = [

    url(r'^', include(router.urls)),
    path('course-auto-suggestion-text', auto_complete.TextAPIView.as_view()),
    # path('course-auto-suggestion', auto_complete.SpecializationDisciplineSuggestionView.as_view()),
    # path('course-auto-suggestion', auto_complete.SpecializationList.as_view()),
    path('course-auto-suggestion', auto_complete.TextAPIView.as_view()),
    path('location-auto-suggestion', auto_complete.LocationAPIView.as_view()),
    path('site-suggestion', auto_complete.GenaricSuggestionAPIView.as_view()),
    path('search', auto_complete.AllSearch.as_view()),
    path('institute-suggestion', auto_complete.InstitutesSearch.as_view()),
    # payments
    path('jazzcash_payment', JazzCashPayment.as_view()),

]
