from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('assignments/<str:initials>/', views.assignments, name='assignments'),
    path('annotate/<str:initials>/<str:rebuttal>/<int:index>/', views.annotate, name='annotate'),
    path('annotate_review/<str:initials>/<str:rebuttal>/',
        views.annotate_review, name='annotate_review'),
    path('agreement/', views.agreement, name='agreement'),
    path('submitted/', views.submitted, name='submitted'),
]
