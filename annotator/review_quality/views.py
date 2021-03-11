from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Annotation, Annotator, AnnotatorAssignment, CommentPair, Sentence
from .forms import AnnotationForm

import collections
import json

QUESTIONS = [
    ("importance", "Did the reviewer discuss the importance of the research question?", "Not at all", "Discussed extensively"),
    ("originality", "Did the reviewer discuss the originality of the paper?", "Not at all", "Discussed extensively with references" ),
    ("strengths_weaknesses", "Did the reviewer clearly identify the strengths and weaknesses of the method (study design, data colletion and data analysis)?", "Not at all", "Comprehensive" ),
    ("useful_comments", "Did the reviewer make specific useful comments on the writing, organisation, tables and figures of the manuscript?", "Not at all",  "Extensive"),
    ("constructive", "Were the reviewer’s comments constructive?", "Not at all",  "Very constructive"),
    ("evidence", "Did the reviewer supply appropriate evidence using examples from the paper to substantiate their comments?", "No comments substantiated",  "All comments substantiated"),
    ("interpretation", "Did the reviewer comment on the author’s interpretation of the results?", "Not at all",  "Discussed extensively"),
    ("overall", "How would you rate the quality of this review overall?", "Poor", "Excellent" ),
    ]

def index(request):
    template = loader.get_template('review_quality/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))

def assignments(request, annotator_initials):
    name = Annotator.objects.get(initials=annotator_initials).name
    assignment_list = AnnotatorAssignment.objects.filter(
            annotator_initials=annotator_initials)
    examples = []
    for assignment in assignment_list:
        relevant_comment_pair = CommentPair.objects.get(
            dataset=assignment.dataset,
            example_index=assignment.example_index)
        maybe_done = Annotation.objects.filter(
        review_sid=relevant_comment_pair.review_sid,
        annotator_initials=annotator_initials)
        if maybe_done:
            is_done = "Completed"
        else:
            is_done = "Incomplete"
        examples.append({"reviewer": relevant_comment_pair.reviewer,
                        "title": relevant_comment_pair.title,
                        "review_sid": relevant_comment_pair.review_sid,
                         "status": is_done})
    template = loader.get_template('review_quality/assignment.html')
    context = {"examples": examples, "name":name}
    return HttpResponse(template.render(context, request))

def get_htmlified_sentences(supernote_id):
    sentences = Sentence.objects.filter(comment_sid=supernote_id)
    final_sentences = []
    for i, sentence in enumerate(sentences):
        final_sentences.append({
            "text":sentence.text + sentence.suffix,
            "idx": i})
    return final_sentences

def annotate(request, review):

    relevant_comment_pair = CommentPair.objects.filter(
            review_sid=review)[0]
    title = relevant_comment_pair.title
    reviewer = relevant_comment_pair.reviewer

    review_sentences = get_htmlified_sentences(review)
    q_list = [{"kw":a, "text":b, "min":c, "max":d} for a,b,c,d in QUESTIONS]


    form = AnnotationForm()
    context = {
            "metadata": {
            "paper_title": title,
            "reviewer": reviewer,
            "forum_id": relevant_comment_pair.forum_id,
            "review_sid": relevant_comment_pair.review_sid,
            },
            "review_sentences": review_sentences,
            "questions": q_list,
            "form": form
            }
    template = loader.get_template('review_quality/annotate.html')
    return HttpResponse(template.render(context, request))

def submitted(request):
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        metadata= annotation_obj["metadata"]

        label_map = {}
        for label in annotation_obj["labels"]:
            location, value = label.split("|")
            label_map[location] = value

        annotation = Annotation(
            importance=label_map["importance"],
            originality=label_map["originality"],
            strengths_weaknesses=label_map["strengths_weaknesses"],
            useful_comments=label_map["useful_comments"],
            constructive=label_map["constructive"],
            evidence=label_map["evidence"],
            interpretation=label_map["interpretation"],
            overall=label_map["overall"],
            comment=annotation_obj["comment"],
            annotator_initials=annotation_obj["annotator"],
            review_sid=metadata["review_sid"]
            )
        annotation.save()

    template = loader.get_template('review_quality/submitted.html')
    return HttpResponse(template.render({}, request))
