from django.shortcuts import render

from .models import *

import collections

LikertQuestion = collections.NamedTuple("LikertQuestion",
        "keyword question min_label max_label".split())
MultipleChoiceQuestion = collections.NamedTuple("MultipleChoiceQuestion",
        "keyword question options_with_keywords")

LIKERT_QUESTIONS = [
    LikertQuestion("importance", "Did the reviewer discuss the importance of the research question?", "Not at all", "Discussed extensively"),
    LikertQuestion("originality", "Did the reviewer discuss the originality of the paper?", "Not at all", "Discussed extensively with references" ),
    LikertQuestion("method", "Did the reviewer clearly identify the strengths and weaknesses of the method (study design, data colletion and data analysis)?", "Not at all", "Comprehensive" ),
    LikertQuestion("presentation", "Did the reviewer make specific useful comments on the writing, organisation, tables and figures of the manuscript?", "Not at all",  "Extensive"),
    LikertQuestion("constructiveness", "Were the reviewer’s comments constructive?", "Not at all",  "Very constructive"),
    LikertQuestion("evidence", "Did the reviewer supply appropriate evidence using examples from the paper to substantiate their comments?", "No comments substantiated",  "All comments substantiated"),
    LikertQuestion("interpretation", "Did the reviewer comment on the author’s interpretation of the results?", "Not at all",  "Discussed extensively"),
    LikertQuestion("reproducibility", "Did the reviewer comment on the reproducibility of the results?", "Not at all",  "Discussed extensively"),
    LikertQuestion("overall", "How would you rate the quality of this review overall?", "Poor", "Excellent" ),
 ]

MC_QUESTIONS = [
        MultipleChoiceQuestion(
            "metareview", "Is this review mentioned in the meta-review?",
            [("no", "Not at all"),
             ("yes-disagree", "Yes, but meta-review disagrees with the review"),
             ("yes-neither", "Yes, and meta-review neither agrees nor disagrees with the review"),
             ("yes-agree", "Yes, and meta-review agrees with the review")
            ])
]


def index(request):
    template = loader.get_template('review_quality/index.html')
    context = {"annotators": Annotator.objects.all()}
    return HttpResponse(template.render(context, request))


def assignments(request, annotator_initials):
    name = Annotator.objects.get(initials=annotator_initials).name
    assignment_list = Assignment.objects.filter(
            annotator_initials=annotator_initials)
    examples = []
    for assignment in assignment_list:
        relevant_comment_pair = Review.objects.get(
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
    annotator = {
            "name": name,
            "initials": initials
            }
    template = loader.get_template('review_quality/assignment.html')
    context = {"examples": examples, "annotator":annotator}
    return HttpResponse(template.render(context, request))


def get_htmlified_sentences(supernote_id):
    chunks = Chunk.objects.filter(
            comment_sid=supernote_id).order_by('chunk_index')
    return "".join(chunks)


def annotate(request, review, annotator):

    relevant_comment_pair = CommentPair.objects.filter(
            review_sid=review)[0]
    title = relevant_comment_pair.title
    reviewer = relevant_comment_pair.reviewer

    review_sentences = "".join(Chunk.objects.filter(
            comment_sid=supernote_id).order_by('chunk_index')) 

    form = AnnotationForm()
    context = {
            "paper_title": title,
            "reviewer": reviewer,
            "forum_id": relevant_comment_pair.forum_id,
            "review_sid": relevant_comment_pair.review_sid,
            "review_text": review_sentences,
            "likert_questions": LIKERT_QUESTIONS,
            "mc_questions": MC_QUESTIONS,
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
            ratings=annotation_obj["ratings"],
            comment=annotation_obj["comment"],
            annotator_initials=annotation_obj["annotator"],
            review_sid=metadata["review_sid"]
            )
        annotation.save()

    template = loader.get_template('review_quality/submitted.html')
    return HttpResponse(template.render({}, request))
