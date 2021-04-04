from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('assignments/<str:initials>/', views.assignments, name='assignments'),
    path('ann_rebuttal/<str:initials>/<str:rebuttal>/<int:index>/',
         views.annotate_rebuttal,
         name='ann_rebuttal'),
    path('ann_review/<str:initials>/<str:review>/',
         views.annotate_review,
         name='ann_review'),
    #path('agreement/', views.agreement, name='agreement'),
    path('submitted/', views.submitted, name='submitted'),
    path('rebuttal_submitted/', views.rebuttal_submitted, name='rebuttal_submitted'),
]
