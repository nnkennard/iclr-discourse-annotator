from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *
from .forms import AnnotationForm

import collections
import json
import yaml

def get_labels():
    with open("zune/zune_data/labels.yaml", 'r') as f:
        return yaml.safe_load(f)

LABELS = get_labels()

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

EMPTY_LABEL_LIST = ["--"]

def format_review_labels():
    original_labels = LABELS["review_relations"]
    label_map = collections.defaultdict(list)
    label_map["top"] = ["-- Arg type"]
    for item in original_labels[0]["subcategories"]:
        label_map["top"].append(item["name"])
    for item in original_labels[1]["subcategories"]:
        label_map["top"].append(item["name"])
    label_map["aspect"] = EMPTY_LABEL_LIST + original_labels[2]["subcategories"]
    label_map["grounding"] = EMPTY_LABEL_LIST + original_labels[3]["subcategories"]
    label_map["polarity"] = EMPTY_LABEL_LIST + original_labels[4]["subcategories"]
    label_map["review_type"] = []
    return label_map

FORMATTED_LABELS = format_review_labels()

def annotate_review(request, review, initials):

    example = Example.objects.get(review_id=review)
    review_sentences = get_htmlified_sentences(review)
    template = loader.get_template('zune/annotate_review.html')
    return HttpResponse(
            template.render(
                {"text": {"review_sentences": review_sentences},
                "labels": FORMATTED_LABELS,
                "form": AnnotationForm(),
                "metadata":{
                    "paper_title": example.title,
                    "initials": initials,
                    "reviewer": example.reviewer,
                    "forum_id": example.forum_id,
                    "review_id": example.review_id}
            }, request))


def submitted(request):
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        metadata = annotation_obj["metadata"]

        review_annotation = ReviewAnnotation(
                review_id=metadata["review_id"],
                overall_comment=annotation_obj["comments"],
                is_valid=True,
                errors="",
                initials=metadata["initials"],
                time_to_annotate=annotation_obj["time_to_annotate"],
                time_of_submission=0,
                )
        review_annotation.save()

        for i, sentence_annotation in enumerate(annotation_obj["labels"]):
            sentence_annotation = ReviewSentenceAnnotation(
                review_id=metadata["review_id"],
                review_sentence_index=i,
                initials=metadata["initials"],
                labels = json.dumps(sentence_annotation)
                    )
            sentence_annotation.save()

        template = loader.get_template('zune/submitted.html')
    return HttpResponse(
            template.render(
                {"initials":annotation_obj["metadata"]["initials"]},
                request))


