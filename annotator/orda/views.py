from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import *

from .orda_utils import *

# Create your views here.

def index(request):
  template = loader.get_template('orda/index.html')
  context = {"annotators": Annotator.objects.all()}
  return HttpResponse(template.render(context, request))


def assignments(request, initials):

  annotator_name = Annotator.objects.get(initials=initials).name
  previously_completed, assignments_to_show = get_this_annotator_assignments(initials)
  presentation_examples = [make_presentation_example(a) for a in assignments_to_show]
  template = loader.get_template('orda/assignment.html')
  context = {
  	  "previously_completed": previously_completed,
      "examples": presentation_examples,
      "annotator": {
          "name": annotator_name,
          "initials": initials
      }
  }
  return HttpResponse(template.render(context, request))

def annotate_review(request, review_id, initials):
  example = Example.objects.get(review_id=review_id)
  review_sentences = get_htmlified_sentences(review_id)
  template = loader.get_template('orda/annotate_review.html')
  return HttpResponse(
      template.render(
          {
              "text": {
                  "review_sentences": review_sentences
              },
              "labels": FORMATTED_LABELS,
              "form": AnnotationForm(),
              "menu_map": ALLOWED_MENUS,
              "metadata": {
                  "paper_title": example.title,
                  "initials": initials,
                  "reviewer": example.reviewer,
                  "forum_id": example.forum_id,
                  "review_id": example.review_id
              }
          }, request))

def review_submitted(request):
    pass


def annotate_rebuttal(request, review_id, initials, index):
  context = get_annotation_context(initials, rebuttal, review_id, index)
  context.update({
      "alignment_errors": LABELS["alignment_errors"],
      "labels": REBUTTAL_RELATIONS,
      "form": AnnotationForm(),
      "metadata": {
          "paper_title": example.title,
          "initials": initials,
          "reviewer": example.reviewer,
          "forum_id": example.forum_id,
          "rebuttal_id": rebuttal,
          "review_id": example.review_id,
          "rebuttal_index": index
      }
  })
  template = loader.get_template('orda/annotate_rebuttal.html')
  return HttpResponse(template.render(context, request))


def rebuttal_submitted(request):
    pass

def agreement(request):
    pass

