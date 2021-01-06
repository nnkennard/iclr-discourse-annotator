from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submitted/', views.submitted, name='submitted'),
    path('<str:review>_<str:rebuttal>/', views.detail, name='detail'),
]


