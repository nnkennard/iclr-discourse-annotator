from django.contrib import admin
from .models import AlignmentAnnotation, AnnotatedPair


admin.site.register(AlignmentAnnotation)
admin.site.register(AnnotatedPair)
