from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submitted/', views.submitted, name='submitted'),
    path('assignments/<str:annotator_initials>/', views.assignments, name='assignments'),
    path('<str:review>/', views.annotate, name='annotate'),
]
