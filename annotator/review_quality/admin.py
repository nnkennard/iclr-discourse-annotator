from django.contrib import admin
from .models import *

for model_name in [Sentence, Annotator, AnnotatorAssignment, CommentPair,
        Annotation]:
    admin.site.register(model_name)


# Register your models here.
