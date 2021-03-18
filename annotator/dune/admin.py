from django.contrib import admin
from .models import *

for model_name in [Sentence, Annotator, AnnotatorAssignment, Example,
        AlignmentAnnotation, AlignmentPairAnnotation]:
    admin.site.register(model_name)
