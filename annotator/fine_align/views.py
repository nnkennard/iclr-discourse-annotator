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
        #temp["previous_annotators"] =  ", ".join([
        #        sorted(set(x["annotator"]
        #        for x in AlignmentAnnotation.objects.values("annotator").filter(
        #            review_supernote=temp["review"],
        #            rebuttal_supernote=temp["rebuttal"],
        #        ).values()
        #       ))])
        temp["previous_annotators"] = ""
        examples.append(temp)
    template = loader.get_template('fine_align/index.html')
    context = {"examples": examples,}
    return HttpResponse(template.render(context, request))


def crunch_supernote(supernote):
    rows = Text.objects.filter(comment_supernote=supernote)
    chunks = []
    current_chunk = []
    current_chunk_idx = 0
    for row in rows:
        if current_chunk_idx == row.chunk_idx:
            current_chunk.append(row.token)
        else:
            if current_chunk == ["NEWLINE"]:
                chunks.append([])
            else:
                chunks.append(current_chunk)
            current_chunk = [row.token]
            current_chunk_idx = row.chunk_idx

    if current_chunk == ["NEWLINE"]:
        chunks.append([])
    else:
        chunks.append(current_chunk)

    return zip(*[(i, " ".join(chunk))
        for i, chunk in enumerate(chunks)
        if chunk])

def detail(request, review, rebuttal):
    review_indices, review_text = crunch_supernote(review)
    rebuttal_indices, rebuttal_text = crunch_supernote(rebuttal)
    title = AnnotatedPair.objects.get(
            review_supernote=review, rebuttal_supernote=rebuttal).title
    context = {
            "paper_title":title,
            "review_text": review_text,
            "rebuttal_text": rebuttal_text,
            "review_indices": review_indices,
            "rebuttal_indices": rebuttal_indices,
            "review": review,
            "rebuttal": rebuttal,
            "codes": CODES}
    template = loader.get_template('fine_align/detail.html')
    return HttpResponse(template.render(context, request))


def submitted(request):
    template = loader.get_template('fine_align/submitted.html')
    form = AnnotationForm(request.POST)
    if form.is_valid():
        annotation_obj = json.loads(form.cleaned_data["annotation"])
        print(annotation_obj)
        
        for rebuttal_chunk_idx, review_chunk_map in annotation_obj["alignments"].items():
            label = "|".join(str(i) for i in review_chunk_map)
            if label:
                annotation = AlignmentAnnotation(
                        review_supernote = annotation_obj["review_supernote"],
                        rebuttal_supernote = annotation_obj["rebuttal_supernote"],
                        rebuttal_chunk = int(rebuttal_chunk_idx),
                        annotator = annotation_obj["annotator"],
                        label = label,
                        comment = annotation_obj["comments"],
                        review_chunking_error = int(rebuttal_chunk_idx) in annotation_obj["errors"]["review_errors"],
                        rebuttal_chunking_error = int(rebuttal_chunk_idx) in annotation_obj["errors"]["rebuttal_errors"],
                        )
                annotation.save()
    context = {}
    return HttpResponse(template.render(context, request))
