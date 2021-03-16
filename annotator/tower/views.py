from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Annotator, AnnotatorAssignment, Example, Sentence, SentenceAnnotation
from .forms import AnnotationForm

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
{"label": "No context", "keyword": "no-context", "checked": False},
{"label": "Global context", "keyword": "global-context", "checked": False},
{"label": "Context is in rebuttal", "keyword": "rebuttal-context", "checked": False},
{"label": "Cannot determine context", "keyword": "cant-determine", "checked": False},
{"label": "Aligned sentences have been highlighted", "keyword": "some-align", "checked": False},
]


def index(request):
    template = loader.get_template('tower/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def assignments(request, annotator_initials):
    name = Annotator.objects.get(initials=annotator_initials).name
    assignment_list = AnnotatorAssignment.objects.filter(
            annotator_initials=annotator_initials)
    display_examples = []
    for assignment in assignment_list:
        examples = Example.objects.filter(
            dataset=assignment.dataset,
            example_index=assignment.example_index)
        relevant_comment_pair = examples[0]

        this_pair_annotations = SentenceAnnotation.objects.filter(
        rebuttal_sid=relevant_comment_pair.rebuttal_sid,
        annotator_initials=annotator_initials)

        if not this_pair_annotations:
            status = "Not started"
        elif len(this_pair_annotations) == len(examples):
            status = "Completed"
        else:
            assert len(this_pair_annotations) < len(examples)
            status = "Started"
    

        display_examples.append({"reviewer": relevant_comment_pair.reviewer,
                        "title": relevant_comment_pair.title,
                         "rebuttal_sid": relevant_comment_pair.rebuttal_sid,
                         "is_done": status})
    template = loader.get_template('tower/assignment.html')
    context = {"examples": display_examples, "name":name, "initials":annotator_initials}
    return HttpResponse(template.render(context, request))

def get_htmlified_sentences(supernote_id):
    sentences = Sentence.objects.filter(comment_sid=supernote_id)
    final_sentences = []
    for i, sentence in enumerate(sentences):
        final_sentences.append({
            "text":sentence.text + sentence.suffix,
            "idx": i})
    return final_sentences


def annotate(request, rebuttal, initials, index):

    relevant_comment_pair = Example.objects.get(
            rebuttal_sid=rebuttal, rebuttal_index=index)
    title = relevant_comment_pair.title
    reviewer = relevant_comment_pair.reviewer

    review_sentences = get_htmlified_sentences(relevant_comment_pair.review_sid)
    rebuttal_sentences = get_htmlified_sentences(rebuttal)

    form = AnnotationForm()

    context = {
            "page_keys": {
                "rebuttal_index": index,
                "initials": initials,
                },
            "review_sentences": review_sentences,
            "rebuttal_sentences": rebuttal_sentences,
            "rebuttal_sentence": rebuttal_sentences[index],
            "label_rows": LABEL_ROWS,
            "no_align_reasons": NO_ALIGN_REASONS,
            "form": form,
            "metadata":{
                "paper_title": title,
                "reviewer": reviewer,
                "forum_id": relevant_comment_pair.forum_id,
                "rebuttal_sid": relevant_comment_pair.rebuttal_sid,
                "review_sid": relevant_comment_pair.review_sid,
            "rebuttal_statuses": ["Incomplete" for _ in range(len(rebuttal_sentences))],
                "rebuttal_index": index}
            }
    template = loader.get_template('tower/annotate.html')
    return HttpResponse(template.render(context, request))
 
