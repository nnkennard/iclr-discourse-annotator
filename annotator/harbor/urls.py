from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agreement/', views.agreement, name='agreement'),
    path('submitted/', views.submitted, name='submitted'),
    path(
        'assignments/<str:annotator_initials>/<str:conference>/',
        views.assignments, name='assignments'),
    path('annotate/<str:annotator_initials>/<str:review_id>/',
        views.annotate, name='annotate'),
]
