from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *
from .forms import AnnotationForm

import collections
import json
import yaml

ARG_TYPES = "Evaluative Request Question Fact Non-arg Summary".split()
ASPECTS = "Motivation/Impact,Originality,Soundness,Substance,Replicability,Meaningful Comp.,Clarity".split(",")
GROUNDING = "Whole paper,Method,Analysis,References".split(",")
POLARITIES = "P-Positive U-Neutral N-Negative".split()

def get_labels():
    with open("dune_data/labels.yaml", 'r') as f:
        return yaml.safe_load(f)

def make_presentation_example(assignment):
    examples = Example.objects.filter(
            rebuttal_id=assignment.rebuttal_id).order_by("reviewer")
    maybe_done = AlignmentAnnotation.objects.filter(
        rebuttal_id=assignment.rebuttal_id,
        initials=assignment.initials).values(
                "rebuttal_sentence_index").distinct()
    if not maybe_done:
        status = "Not started"
    elif len(maybe_done) == len(examples):
        status = "Complete"
    else:
        status = "Incomplete"
    example = examples[0]
    return {
            "reviewer": example.reviewer,
            "num_done": str(len(maybe_done)) + " / " + str(len(examples)),
            "title": example.title,
            "rebuttal_id": example.rebuttal_id,
            "status": status}


def get_htmlified_sentences(supernote_id):
    sentences = Sentence.objects.filter(comment_id=supernote_id)
    final_sentences = []
    for i, sentence in enumerate(sentences):
        final_sentences.append({
            "text":sentence.text + sentence.suffix,
            "idx": i})
    return final_sentences


def index(request):
    template = loader.get_template('dune/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def assignments(request, initials):
    annotator = Annotator.objects.get(initials=initials)
    presentation_examples = [make_presentation_example(assignment)
        for assignment in AnnotatorAssignment.objects.filter(
           initials=initials).order_by("id")]
    template = loader.get_template('dune/assignment.html')
    context = {
        "examples": presentation_examples,
        "annotator": {"name": annotator.name, "initials": annotator.initials}}
    return HttpResponse(template.render(context, request))


PartialRow = collections.namedtuple("CompletedRow",
    "title reviewer completed incomplete")

def get_partial_row(rebuttal_id):
    example = Example.objects.filter(rebuttal_id=rebuttal_id)[0]

    assignments = AnnotatorAssignment.objects.filter(rebuttal_id=rebuttal_id)
    complete = []
    incomplete = []
    for assignment in assignments:
        if AlignmentAnnotation.objects.filter(
            initials=assignment.initials, rebuttal_id=rebuttal_id):
            complete.append(assignment.initials)
        else:
            incomplete.append(assignment.initials)
    return PartialRow(example.title, example.reviewer, 
        ", ".join(complete),  ", ".join(incomplete))._asdict()

def agreement(request):
    examples = Example.objects.all()
    
    completed_rows = []
    partial_rows = []
    for example in examples:
        relevant_annotations = AlignmentAnnotation.objects.filter(rebuttal_id=example.rebuttal_id)
        annotators = set([ann.initials for ann in relevant_annotations])
        if len(annotators) == 2:
            ann1, ann2 = annotators
            completed_rows.append(
                get_completed_row(review.review_id, ann1, ann2))
        elif len(annotators) == 1:
            partial_rows.append(get_partial_row(example.rebuttal_id))
        else:
            pass
    template = loader.get_template('harbor/agreement.html')
    return HttpResponse(template.render({"completed":completed_rows,
        "partial":partial_rows}, request))

def get_annotation_context(initials, rebuttal_id, review_id, index):
    this_annotator_annotations = [x["rebuttal_sentence_index"]
                                    for x in AlignmentAnnotation.objects.filter(
            initials=initials,
            rebuttal_id=rebuttal_id).values("rebuttal_sentence_index")]

    rebuttal_sentences = get_htmlified_sentences(rebuttal_id)
    statuses = [i in this_annotator_annotations for i in range(len(rebuttal_sentences))]

    maybe_previous_annotation = AlignmentAnnotation.objects.filter(
            initials=initials,
            rebuttal_id=rebuttal_id, rebuttal_sentence_index=index
            -1).order_by("-id")
    if maybe_previous_annotation:
        previous_annotation = maybe_previous_annotation[0].aligned_review_sentences
    else:
        previous_annotation = ""

    return {
        "text": {
            "review_sentences": get_htmlified_sentences(review_id),
            "rebuttal_sentences": rebuttal_sentences,
            "rebuttal_sentence": rebuttal_sentences[index],
        },
        "other_annotations": {
            "statuses": statuses,
            "previous_alignment": previous_annotation
        }
    }

def annotate(request, rebuttal, initials, index):
    example = Example.objects.get(
            rebuttal_id=rebuttal,
            rebuttal_sentence_index=index)
    context = get_annotation_context(initials, rebuttal, example.review_id, index)
    context.update( {
        "labels": get_labels(),
        "form": AnnotationForm(),
        "metadata":{
            "paper_title": example.title,
            "initials": initials,
            "reviewer": example.reviewer,
            "forum_id": example.forum_id,
            "rebuttal_id": rebuttal,
            "review_id": example.review_id,
            "rebuttal_index": index}
            })
    template = loader.get_template('dune/annotate.html')
    return HttpResponse(template.render(context, request))

def submitted(request):
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        metadata = annotation_obj["metadata"]
        print(annotation_obj["metadata"])

        aligned_review_sentences = "|".join(sorted(str(i) for i, val in
                enumerate(annotation_obj["alignment_labels"]) if val))

        annotation = AlignmentAnnotation(
                rebuttal_id=metadata["rebuttal_id"],
                rebuttal_sentence_index=metadata["rebuttal_index"],
                initials=metadata["initials"],
                is_valid=True,
                aligned_review_sentences=aligned_review_sentences,
                relation_label=annotation_obj["relation_label"],
                comment=annotation_obj["comment"],
                alignment_errors=annotation_obj["alignment_errors"],
                time_to_annotate=annotation_obj["time_to_annotate"],
           )
        annotation.save()

        maybe_next_index = annotation_obj["metadata"]["rebuttal_index"] + 1
        if (maybe_next_index ==
            annotation_obj["num_rebuttal_sentences"]):
            next_sentence_info = {"valid":False,
                    "initials":metadata["initials"]}
        else:
            next_sentence_info = {
                    "rebuttal_sentence_index":maybe_next_index,
                    "initials":metadata["initials"],
                    "rebuttal_id":metadata["rebuttal_id"],
                    "valid": True}

    template = loader.get_template('dune/submitted.html')
    return HttpResponse(
            template.render(
                {"next_sentence_info":next_sentence_info},
                request))

def annotate_review(request, rebuttal, initials):

    example = Example.objects.get(
            rebuttal_id=rebuttal,
            rebuttal_sentence_index=0)
    review_sentences = get_htmlified_sentences(example.review_id)
    template = loader.get_template('dune/annotate_review.html')
    return HttpResponse(
            template.render(
                {"text": {"review_sentences": review_sentences},
                "arg_types": ARG_TYPES,
                "aspects": ASPECTS,
                "polarities": POLARITIES,
                "groundings": GROUNDING,
                "metadata":{
                    "paper_title": example.title,
                    "initials": initials,
                    "reviewer": example.reviewer,
                    "forum_id": example.forum_id,
                    "rebuttal_id": rebuttal,
                    "review_id": example.review_id}
            }, request))
