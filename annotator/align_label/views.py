from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Annotator, AnnotatorAssignment, CommentPair, Sentence

import collections

LABELS  = collections.OrderedDict({
    "Action": collections.OrderedDict({
        "Answer": ["Direct", "Elaborate", "Follow-up question"],
        "Non-compliance ": ["Premise wrong", "Can't fix", "Already answered"],
        "Change": ["Already completed", "Promised by CR", "Promised, no time frame"],
    }),
    "Non-action": collections.OrderedDict({
        "Structuring": ["Quote", "Subheading", "Summary"],
        "Politeness": ["Thanking", "Acknowledgement"]
    })
})

colors = ["red2"] * 3 + ["orange1"] * 3 + ["yellow"] * 3 + ["green3"] * 3 + ["blue1"] * 2

LABEL_ROWS = []
for category, subcategory_map in LABELS.items():
    for subcategory, labels in subcategory_map.items():
        for label in labels:
            LABEL_ROWS.append({"label":label,
                         "subcategory":subcategory,
                         "category":category,
                         "color": colors.pop(0)})

NO_ALIGN_REASONS = [
{"label": "No context", "keyword": "no-context", "checked": False},
{"label": "Global context", "keyword": "global-context", "checked": False},
{"label": "Context is in rebuttal", "keyword": "rebuttal-context", "checked": False},
{"label": "Aligned sentences have been highlighted", "keyword": "some-align", "checked": True},
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

    context = {
            "paper_title": title,
            "reviewer": reviewer,
            "review_sentences": review_sentences,
            "rebuttal_sentences": rebuttal_sentences,
            "label_rows": LABEL_ROWS,
            "no_align_reasons": NO_ALIGN_REASONS
            }
    template = loader.get_template('align_label/annotate.html')
    return HttpResponse(template.render(context, request))
    
