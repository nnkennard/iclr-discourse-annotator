import json

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import AlignmentAnnotation, AnnotatedPair, Text
#from .forms import AnnotationForm

def index(request):
    pair_list = AnnotatedPair.objects.all()
    examples = []
    for obj in pair_list:
        temp = dict(obj.__dict__)
        del temp["_state"]
        print(AlignmentAnnotation.objects.all())
        #temp["previous_annotators"] =  ", ".join([
        #        sorted(set(x["annotator"]
        #        for x in AlignmentAnnotation.objects.values("annotator").filter(
        #            review_supernote=temp["review"],
        #            rebuttal_supernote=temp["rebuttal"],
        #        ).values()
        #       ))])
        temp["previous_annotators"] = ""
        examples.append(temp)
    template = loader.get_template('fine_align/index.html')
    context = {"examples": examples,}
    return HttpResponse(template.render(context, request))

