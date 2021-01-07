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
        Code("no_context", "There is no relevant context span for this rebuttal chunk")._asdict(),
        Code("global_context", "This rebuttal chunk is a response to the review as a whole ")._asdict(),
        ]],
    ["Deixis", [
        Code("review_deixis", "There exists a deictic mention referring to this chunk's context")._asdict(),
        Code("rebuttal_deixis", "This rebuttal chunk refers to another part of the rebuttal")._asdict(),
    ]]
]


def index(request):
    pair_list = AnnotatedPair.objects.all()
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
        "-LSB-", "[").replace(
        "-RSB-", "]")


def double_crunch_rows(supernote):
    rows = Text.objects.filter(comment_sid=supernote)
    print(len(rows))
    chunks = []
    current_chunk = []
    current_chunk_idx = 0
    current_sentence = []
    current_sentence_idx = 0
    for i, row in enumerate(rows):
        print(i)
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
    print(temp_rebuttal_chunks)
    print("-" * 20)
    rebuttal_chunks = [" ".join(chunk) for chunk in double_crunch_rows(rebuttal)]
    print(rebuttal)
    print(rebuttal_chunks)
    print("-" * 80)
    if not rebuttal_chunks:
        dsds

    title = AnnotatedPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal).title
    reviewer = AnnotatedPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal).reviewer

    context = {
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
        review_chunks, start_map, end_map = get_review_metadata(annotation_obj["review_sid"])
        for alignment in annotation_obj["alignments"]:
          rebuttal_chunk_idx, start_token, end_token, error = alignment
          annotation = AlignmentAnnotation(
            review_sid = annotation_obj["review_sid"],
            rebuttal_sid = annotation_obj["rebuttal_sid"],
            annotator = annotation_obj["annotator"],
            comment = annotation_obj["comment"],
            rebuttal_chunk_idx = rebuttal_chunk_idx,
            review_start_idx = start_token,
            review_exclusive_end_idx = end_token,
            error=error,
            )
          annotation.save()
    return HttpResponse(template.render({}, request))
