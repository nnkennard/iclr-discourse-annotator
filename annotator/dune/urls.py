from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('assignments/<str:initials>/', views.assignments, name='assignments'),
    path('annotate/<str:initials>/<str:rebuttal>/<int:index>/', views.annotate, name='annotate'),
    path('agreement/', views.agreement, name='agreement'),
    path('submitted/', views.submitted, name='submitted'),
]
