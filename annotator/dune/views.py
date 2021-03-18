from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *

from django.shortcuts import render

def index(request):
    template = loader.get_template('dune/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))

def assignments(request, initials):
    name = Annotator.objects.get(initials=initials).name
    assignment_list = AnnotatorAssignment.objects.filter(
           annotator_initials=initials).order_by("id")

    presentation_examples = []
    for assignment in assignment_list:
        print(assignment.rebuttal_id)
        examples = Example.objects.filter(
            rebuttal_id=assignment.rebuttal_id)
        print("Number of examples")
        print(len(examples))
        maybe_done = AlignmentAnnotation.objects.filter(
        rebuttal_id=assignment.rebuttal_id,
        annotator_initials=initials).values(
                "rebuttal_sentence_index").distinct()
        if not maybe_done:
            is_done = "Not started"
        elif len(maybe_done) == len(examples):
            is_done = "Complete"
        else:
            is_done = "Incomplete"
        presentation_examples.append({"reviewer": examples[0].reviewer,
                        "title": examples[0].title,
                        "rebuttal_id": examples[0].rebuttal_id,
                         "status": is_done})
    annotator = {
            "name": name,
            "initials": initials
            }
    template = loader.get_template('dune/assignment.html')
    context = {"examples": presentation_examples, "annotator":annotator}
    return HttpResponse(template.render(context, request))



def annotate(request):
    return HttpResponse("Hi")

def agreement(request):
    return HttpResponse("Hi")

def submitted(request):
    return HttpResponse("Hi")



