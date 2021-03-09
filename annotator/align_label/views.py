from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Annotator, AnnotatorAssignment, CommentPair, Sentence, SentenceAnnotation
from .forms import AnnotationForm

import collections
import json

LABELS  = collections.OrderedDict({
    "Action": collections.OrderedDict({
        "Answer": ["Direct", "Elaborate", "Follow-up question"],
        "Non-compliance ": ["Premise wrong", "Can't fix", "Already answered"],
        "Change": ["Already completed", "Promised by CR", "Promised, no time frame"],
    }),
    "Non-action": collections.OrderedDict({
        "Structuring": ["Quote", "Subheading", "Summary"],
        "Politeness": ["Thanking", "Acknowledgement"]
    }),
    "Error": {"Error": ["None of the above"]},
})

colors = ["red2"] * 3 + ["orange1"] * 3 + ["yellow"] * 3 + ["green3"] * 3 + ["blue1"] * 2 + ["white"]

LABEL_ROWS = []
for category, subcategory_map in LABELS.items():
    if category == "Error":
        checked = True
    else:
        checked = False
    for subcategory, labels in subcategory_map.items():
        for label in labels:
            LABEL_ROWS.append({"label":label,
                         "subcategory":subcategory,
                         "category":category,
                         "color": colors.pop(0),
                         "checked": checked})

NO_ALIGN_REASONS = [
{"label": "No context", "keyword": "no-context", "checked": True},
{"label": "Global context", "keyword": "global-context", "checked": False},
{"label": "Context is in rebuttal", "keyword": "rebuttal-context", "checked": False},
{"label": "Aligned sentences have been highlighted", "keyword": "some-align", "checked": False},
]

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

def get_htmlified_sentences(supernote_id):
    sentences = Sentence.objects.filter(comment_sid=supernote_id)
    final_sentences = []
    for i, sentence in enumerate(sentences):
        final_sentences.append({
            "text":sentence.text + sentence.suffix,
            "idx": i})
    return final_sentences

def annotate(request, review, rebuttal):

    relevant_comment_pair = CommentPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal)
    title = relevant_comment_pair.title
    reviewer = relevant_comment_pair.reviewer

    review_sentences = get_htmlified_sentences(review)
    rebuttal_sentences = get_htmlified_sentences(rebuttal)

    form = AnnotationForm()

    context = {
            "review_sentences": review_sentences,
            "rebuttal_sentences": rebuttal_sentences,
            "label_rows": LABEL_ROWS,
            "no_align_reasons": NO_ALIGN_REASONS,
            "form": form,
            "metadata":{
                "paper_title": title,
                "reviewer": reviewer,
                "forum_id": relevant_comment_pair.forum_id,
                "rebuttal_sid": relevant_comment_pair.rebuttal_sid,
                "review_sid": relevant_comment_pair.review_sid,}
            }
    template = loader.get_template('align_label/annotate.html')
    return HttpResponse(template.render(context, request))
    
def submitted(request):
    form = AnnotationForm(request.POST)
    print(form)
    print(dir(form))
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        metadata= annotation_obj["metadata"]

        label_map = {}
        for error in annotation_obj["errors"]:
            location, value = error.split("|")
            label_map[location] = value

        for rebuttal_i, rebuttal_highlights in enumerate(
                annotation_obj["highlighted"]):
            alignment_label_collector = []
            for review_i, aligned in enumerate(rebuttal_highlights):
                if aligned:
                    alignment_label_collector.append(str(review_i))
            alignment_label = "|".join(alignment_label_collector)
            alignment_error = label_map["align:radios-"+str(rebuttal_i)]
            relation_label = label_map["label:radios-"+str(rebuttal_i)]
            annotation = SentenceAnnotation(
                review_sid = metadata["review_sid"],
                rebuttal_sid = metadata["rebuttal_sid"],
                annotator_initials = annotation_obj["annotator"],    
                rebuttal_sentence_idx = rebuttal_i,
                aligned_review_sentences = alignment_label,
                alignment_comment = "",
                alignment_errors = alignment_error,
                relation = relation_label,
                relation_comment = "",
                relation_errors =  "")
            print(annotation)
            annotation.save()

    template = loader.get_template('align_label/submitted.html')
    return HttpResponse(template.render({}, request))

