from django.contrib import admin

from .models import *

admin.site.register(AlignmentAnnotation)
admin.site.register(AnnotatedPair)

# Register your models here.
