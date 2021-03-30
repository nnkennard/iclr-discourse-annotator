from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *
from .forms import AnnotationForm

import collections
import json

from scipy import stats

import yaml

def get_questions():
    with open("harbor_data/questions.yaml", 'r') as f:
        return yaml.safe_load(f)


def index(request):
    template = loader.get_template('harbor/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def assignments(request, annotator_initials):
    name = Annotator.objects.get(initials=annotator_initials).name
    assignment_list = Assignment.objects.filter(
            annotator_initials=annotator_initials).order_by("review_id")

    examples = []
    for assignment in assignment_list:
        review = Review.objects.get(
            review_id=assignment.review_id)
        maybe_done = Annotation.objects.filter(
        review_id=review.review_id,
        annotator_initials=annotator_initials)
        if maybe_done:
            is_done = "Completed"
        else:
            is_done = "Incomplete"
        examples.append({"reviewer": review.reviewer,
                        "title": review.title,
                        "review_sid": review.review_id,
                         "status": is_done})
    annotator = {
            "name": name,
            "initials": annotator_initials
            }
    template = loader.get_template('harbor/assignment.html')
    context = {"examples": examples, "annotator":annotator}
    return HttpResponse(template.render(context, request))


def get_htmlified_sentences(supernote_id):
    chunks = Chunk.objects.filter(
            comment_sid=supernote_id).order_by('chunk_index')
    return "".join(chunks)


def annotate(request, review_id, annotator_initials):

    review = Review.objects.filter(
            review_id=review_id)[0]
    title = review.title
    reviewer = review.reviewer

    review_sentences = "".join(chunk.text for chunk in Chunk.objects.filter(
            review_id=review_id).order_by('chunk_index')) 

    name = Annotator.objects.get(initials=annotator_initials).name

    form = AnnotationForm()
    context = {
            "paper_title": title,
            "reviewer": reviewer,
            "forum": review.forum,
            "review_id": review.review_id,
            "review_text": review_sentences,
            "questions": get_questions(),
            "form": form,
            "annotator":{"name": name, "initials": annotator_initials}
            }
    template = loader.get_template('harbor/annotate.html')
    return HttpResponse(template.render(context, request))

def submitted(request):
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])

        annotation = Annotation(
            ratings=annotation_obj["ratings"],
            comment=annotation_obj["comment"],
            annotator_initials=annotation_obj["annotator"],
            review_id=annotation_obj["review_id"]
            )
        annotation.save()

    template = loader.get_template('harbor/submitted.html')
    return HttpResponse(template.render({}, request))


CompletedRow = collections.namedtuple("CompletedRow",
    "title reviewer annotators agreement")

def get_likert_labels_in_order(annotation):
    likert_map = {}
    for k,v in json.loads(annotation.ratings).items():
        if k == "metareview" or v == "metareview":
            continue
        likert_map[k] = v
    return [likert_map[k] for k in sorted(likert_map.keys())]

def spearman_wrapper(ann1, ann2):
    labels1 = get_likert_labels_in_order(ann1)
    labels2 = get_likert_labels_in_order(ann2)
    assert len(labels1) == len(labels2)
    return '{0:.3f}'.format(stats.spearmanr(labels1, labels2)[0])
    
def get_completed_row(review_id, annotator1, annotator2):
    ann1 = Annotation.objects.filter(review_id=review_id, annotator_initials=annotator1).order_by('-id')[0]
    ann2 = Annotation.objects.filter(review_id=review_id, annotator_initials=annotator2).order_by('-id')[0]
    review = Review.objects.get(review_id=ann1.review_id)
    annotators = ", ".join(sorted([ann1.annotator_initials, ann2.annotator_initials]))
    #spearman = spearman_wrapper(ann1, ann2)
    spearman = "n/a"
    return CompletedRow(review.title, review.reviewer, annotators, spearman)._asdict()



PartialRow = collections.namedtuple("CompletedRow",
    "title reviewer completed incomplete")

def get_partial_row(review_id):
    review = Review.objects.get(review_id=review_id)

    assignments = Assignment.objects.filter(review_id=review_id)
    complete = []
    incomplete = []
    for assignment in assignments:
        if Annotation.objects.filter(
            annotator_initials=assignment.annotator_initials, review_id=review_id):
            complete.append(assignment.annotator_initials)
        else:
            incomplete.append(assignment.annotator_initials)
    return PartialRow(review.title, review.reviewer, 
        ", ".join(complete),  ", ".join(incomplete))._asdict()

def agreement(request):
    reviews = Review.objects.all()
    
    completed_rows = []
    partial_rows = []
    for review in reviews:
        relevant_annotations = Annotation.objects.filter(review_id=review.review_id)
        annotators = set([ann.annotator_initials for ann in relevant_annotations])
        if len(annotators) == 2:
            ann1, ann2 = annotators
            completed_rows.append(
                get_completed_row(review.review_id, ann1, ann2))
        elif len(annotators) == 1:
            partial_rows.append(get_partial_row(review.review_id))
        else:
            pass
            #assert not relevant_annotations
    print("Completed rows:")
    print(completed_rows)
    template = loader.get_template('harbor/agreement.html')
    return HttpResponse(template.render({"completed":completed_rows,
        "partial":partial_rows}, request))
