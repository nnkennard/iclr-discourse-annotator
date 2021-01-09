import collections
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import AlignmentAnnotation, AnnotatedPair, Text
from .forms import AnnotationForm


Code = collections.namedtuple("Code", ["code", "label"])
CodeList = collections.namedtuple("CodeList", ["list_name", "codes"])


CODES = [
    ["Context", [
        Code("no_context", "There is no relevant context span in the review for this rebuttal chunk")._asdict(),
        Code("rebuttal_context",
            "The context for this rebuttal chunk is elsewhere in the rebuttal")._asdict(),
        Code("global_context", "This rebuttal chunk is a response to the review as a whole ")._asdict(),
        ]],
    ["Special", [
        Code("signpost", "Heading, numbering, or other signposting")._asdict(),
        Code("quote", "Exact quote from review")._asdict(),
        Code("reference", "Reference cited elsewhere in rebuttal")._asdict(),
        ]],

    ["Chunking", [
        Code("should_split",
            "'Sentence' actually contains two or more sentences (please annotate context of both)")._asdict(),
        Code("multiple_units",
            "Single sentence contains multiple discourse units with different contexts (please annotate context of both)")._asdict(),
        Code("major_error",
            "Major error in chunking (unrecoverable) (please comment)")._asdict(),
        ]],
    ["Deixis", [
        Code("no_deixis", "No occurrences of deixis in this chunk")._asdict(),
        Code("review_deixis", "Reference to part of review")._asdict(),
        Code("rebuttal_deixis", "Reference to different part of rebuttal")._asdict(),
        Code("manuscript_deixis", 
            "Reference to part of original manuscript")._asdict(),
        Code("revision_deixis", "Reference to part of revised manuscript")._asdict(),
    ]]
]


def index(request):
    pair_list = AnnotatedPair.objects.filter(
            dataset="traindev_train").order_by(
                    'title', "reviewer")
    examples = []
    for obj in pair_list:
        temp = dict(obj.__dict__)
        del temp["_state"]
        prev_annotators = sorted(
        set(
            [x["annotator"]
             for x in AlignmentAnnotation.objects.values(
              "annotator").filter(
                                    review_sid=temp["review_sid"],
                                    rebuttal_sid=temp["rebuttal_sid"],)]))
        if prev_annotators:
            temp["previous_annotators"] = "|".join(prev_annotators)
        else:
            temp["previous_annotators"] = ""
        examples.append(temp)
    template = loader.get_template('final_align/index.html')
    context = {"examples": examples,}
    return HttpResponse(template.render(context, request))

def process_sentence_tokens(tokens):
    return " ".join(tokens).replace(
        "-LRB-", "(").replace(
        "-RRB-", ")").replace(
        "-LCB-", "{").replace(
        "-RCB-", "}").replace(
        "-LSB-", "[").replace(
        "-RSB-", "]")


def double_crunch_rows(supernote):
    rows = Text.objects.filter(comment_sid=supernote)
    chunks = []
    current_chunk = []
    current_chunk_idx = 0
    current_sentence = []
    current_sentence_idx = 0

    for i, row in enumerate(rows):
        if current_chunk_idx == row.chunk_idx:
            if current_sentence_idx == row.sentence_idx:
                current_sentence.append(row.token)
            else:
                current_chunk.append(process_sentence_tokens(current_sentence))
                current_sentence = [row.token]
                current_sentence_idx = row.sentence_idx
        else:
            current_chunk.append(process_sentence_tokens(current_sentence))
            chunks.append(current_chunk)
            current_chunk = []
            current_sentence = [row.token]
            current_chunk_idx = row.chunk_idx
            assert row.sentence_idx == 0
            current_sentence_idx = 0

    current_chunk.append(process_sentence_tokens(current_sentence))
    chunks.append(current_chunk)

    return chunks


def detail(request, review, rebuttal):
    review_chunks = double_crunch_rows(review)
    review_sentences = []
    sentence_i = 0
    for chunk in review_chunks:
        for sentence in chunk:
            review_sentences.append({"text": sentence, "idx": sentence_i})
            sentence_i += 1
        review_sentences.append({"text": "CHUNK_BREAK", "idx": -1})
    temp_rebuttal_chunks = double_crunch_rows(rebuttal)
    rebuttal_chunks = sum(double_crunch_rows(rebuttal), [])
    if not rebuttal_chunks:
        dsds

    relevant_annotated_pair = AnnotatedPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal)

    title = relevant_annotated_pair.title
    reviewer = relevant_annotated_pair.reviewer
    metadata = {"example_index":relevant_annotated_pair.example_index,
                "dataset":relevant_annotated_pair.dataset,
                "forum_id":relevant_annotated_pair.forum_id,
                "rebuttal_sid": relevant_annotated_pair.rebuttal_sid}

    context = {
            "metadata": metadata,
            "paper_title": title,
            "reviewer": reviewer,
            "review_sentences": review_sentences,
            "rebuttal_chunks": rebuttal_chunks,
            "review": review,
            "rebuttal": rebuttal,
            "codes": CODES}
    template = loader.get_template('final_align/detail.html')
    return HttpResponse(template.render(context, request))


def submitted(request):
    template = loader.get_template('final_align/submitted.html')
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        for i, alignment in enumerate(annotation_obj["alignments"]):
            relevant_errors = annotation_obj["errors"][str(i)]
            aligned_review_indices = None
            if "global_context" in relevant_errors:
                aligned_review_indices = "-1"
            else:
                aligned_review_indices = "|".join(
                      [str(j) for j in sorted(alignment)])
            if not aligned_review_indices:
                assert "no_context" in relevant_errors
            assert aligned_review_indices is not None
            
            annotation = AlignmentAnnotation(
                review_sid = annotation_obj["review_sid"],
                rebuttal_sid = annotation_obj["rebuttal_sid"],
                annotator = annotation_obj["annotator"],
                comment = annotation_obj["comment"],
                rebuttal_chunk_idx=i,
                aligned_review_sentences=aligned_review_indices,
                error="|".join(relevant_errors),
                example_index = annotation_obj["metadata"]["example_index"],
                dataset = annotation_obj["metadata"]["dataset"],
                )
            annotation.save()

    return HttpResponse(template.render({}, request))
