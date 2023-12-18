from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router_1 = DefaultRouter()
router_1.register(r'yogacourses', views.YogaCoursesViewSet)

router_2 = DefaultRouter()
router_2.register(r'yogaslots', views.YogaSlotViewSet)

urlpatterns = [
    path('', include(router_1.urls)),
    path('', include(router_2.urls)),
    path('enroll/', views.enroll, name='enroll'),
    path('enrolled_courses/', views.get_enrolled_courses, name='get_enrolled_courses'),
]

