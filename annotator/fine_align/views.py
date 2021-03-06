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
        Code("mult_spans", "There are multiple non-contiguous spans that form the context for this chunk")._asdict(),
        ]],
    ["Chunking",  [
        Code("merge_next", "Should merge with next chunk")._asdict(),
        Code("merge_prev", "Should merge with previous chunk")._asdict(),
        Code("should_split", "Should be split into multiple chunks")._asdict(),
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
        prev_annotators = sorted(set([x["annotator"] for x in AlignmentAnnotation.objects.values("annotator").filter(
                   review_sid=temp["review_sid"],
                   rebuttal_sid=temp["rebuttal_sid"],
               )]))
        if prev_annotators:
            temp["previous_annotators"] = "|".join(prev_annotators)
        else:
            temp["previous_annotators"] = ""
        examples.append(temp)
    template = loader.get_template('fine_align/index.html')
    context = {"examples": examples,}
    return HttpResponse(template.render(context, request))


def crunch_supernote(supernote):
    """Given a supernote id, returns a list of list of tokens.
    """
    rows = Text.objects.filter(comment_sid=supernote)
    chunks = []
    current_chunk = []
    current_chunk_idx = 0
    for row in rows:
        if current_chunk_idx == row.chunk_idx:
            current_chunk.append(row.token)
        else:
            chunks.append(current_chunk)
            current_chunk = [row.token]
            current_chunk_idx = row.chunk_idx
    chunks.append(current_chunk)
    return chunks

def detail(request, review, rebuttal):
    review_chunks = [" ".join(chunk) for chunk in crunch_supernote(review)]
    rebuttal_chunks = crunch_supernote(rebuttal)
    title = AnnotatedPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal).title
    reviewer = AnnotatedPair.objects.get(
            review_sid=review, rebuttal_sid=rebuttal).reviewer

    nonempty_rebuttal = [(i, " ".join(chunk))
                         for i, chunk in enumerate(rebuttal_chunks)
                         if not chunk == ["<br>"]]
    assert not len(rebuttal_chunks) == len(nonempty_rebuttal)
    nonempty_rebuttal_indices, nonempty_rebuttal_chunks = zip(*nonempty_rebuttal)
    context = {
            "paper_title": title,
            "reviewer": reviewer,
            "review_chunks": review_chunks,
            "nonempty_rebuttal_chunks": nonempty_rebuttal_chunks,
            "rebuttal_indices": nonempty_rebuttal_indices,
            "review": review,
            "rebuttal": rebuttal,
            "codes": CODES}
    template = loader.get_template('fine_align/detail.html')
    return HttpResponse(template.render(context, request))

def get_review_substring(review_chunks, start_map, end_map, start_token, end_token):
    all_tokens = sum(review_chunks, [])
    nonempty_review_tokens = [token for token in sum(review_chunks, []) if not token == "<br>"]
    print(nonempty_review_tokens[start_token:end_token])
    print(all_tokens[start_map[start_token]:end_map[end_token]])

def get_review_metadata(review_sid):    
    review_chunks = crunch_supernote(review_sid)

    all_tokens = sum(review_chunks, [])
    nonempty_tokens = [token for token in all_tokens if not token == "<br>"]

    start_map = list(range(len(nonempty_tokens)))
    end_map = list(range(len(nonempty_tokens)))

    all_i = nonempty_i = 0
    print("x")
    while all_i < len(all_tokens):
        if all_tokens[all_i] == "<br>":
            if nonempty_i + 1 < len(nonempty_tokens):
                end_map[nonempty_i + 1] -= 1
            for j in range (nonempty_i, len(nonempty_tokens)):
                start_map[j] += 1
                end_map[j] += 1
            all_i += 1
        else:
            all_i += 1
            nonempty_i += 1

    print("Got metadata")
    return review_chunks, start_map, end_map



def submitted(request):
    template = loader.get_template('fine_align/submitted.html')
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
