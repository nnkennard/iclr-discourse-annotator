from django.contrib import admin
from .models import *

for model_name in [Annotator, Chunk, Review, Annotation, Assignment]:
    admin.site.register(model_name)
