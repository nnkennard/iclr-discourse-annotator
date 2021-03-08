from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Annotator, AnnotatorAssignment, CommentPair

def index(request):
    template = loader.get_template('align_label/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def assignments(request, annotator_initials):
    name = Annotator.objects.get(initials=annotator_initials).name
    assignment_list = AnnotatorAssignment.objects.filter(
            annotator_initials=annotator_initials)
    examples = []
    for assignment in assignment_list:
        examples.append(CommentPair.objects.get(dataset=assignment.dataset,
            example_index=assignment.example_index))
    template = loader.get_template('align_label/assignment.html')
    context = {"examples": examples, "name":name}
    return HttpResponse(template.render(context, request))

def annotate(request, review, rebuttal):
    context = {}
    template = loader.get_template('align_label/annotate.html')
    return HttpResponse(template.render(context, request))
    
