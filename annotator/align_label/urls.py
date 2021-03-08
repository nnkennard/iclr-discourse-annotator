from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('assignments/<str:annotator_initials>/', views.assignments, name='assignments'),
    path('<str:review>/<str:rebuttal>/', views.annotate, name='annotate'),
]
