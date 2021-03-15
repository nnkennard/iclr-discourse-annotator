from django.contrib import admin
from .models import *

for model_name in [Sentence, Annotator, AnnotatorAssignment, Example,
        SentenceAnnotation, PairAnnotation]:
    admin.site.register(model_name)

