from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *

import yaml

def get_labels():
    with open("zune/zune_data/labels.yaml", 'r') as f:
        return yaml.safe_load(f)


def get_htmlified_sentences(supernote_id):
    sentences = Sentence.objects.filter(comment_id=supernote_id)
    final_sentences = []
    for i, sentence in enumerate(sentences):
        final_sentences.append({
            "text":sentence.text + sentence.suffix,
            "idx": i})
    return final_sentences


def index(request):
    template = loader.get_template('zune/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def make_presentation_example(assignment):
    example = Example.objects.get(
            rebuttal_id=assignment.rebuttal_id)

    review_annotations = ReviewAnnotation.objects.filter(
        review_id=assignment.review_id,
        initials=assignment.initials).order_by("id") # This needs to be related to time of sbmission argh
    if not review_annotations:
        review_status = "Not started"
    elif review_annotations[0].is_valid:
        review_status = "Complete"
    else:
        review_status = "Not completed"
    
    rebuttal_annotations = RebuttalSentenceAnnotation.objects.filter(
        rebuttal_id=assignment.rebuttal_id,
        initials=assignment.initials).order_by("id").values(
                "rebuttal_sentence_index").distinct()

    return {
            "reviewer": example.reviewer,
            "review_status": review_status,
            "rebuttal_status": " / ".join([
                str(len(rebuttal_annotations)),
                str(example.num_rebuttal_sentences),
                ]),
            "title": example.title,
            "rebuttal_id": example.rebuttal_id,
            "review_id": example.review_id,
            }



def assignments(request, initials):
    annotator = Annotator.objects.get(initials=initials)
    presentation_examples = [make_presentation_example(assignment)
        for assignment in AnnotatorAssignment.objects.filter(
           initials=initials).order_by("id")]
    template = loader.get_template('zune/assignment.html')
    context = {
        "examples": presentation_examples,
        "annotator": {"name": annotator.name, "initials": annotator.initials}}
    return HttpResponse(template.render(context, request))


