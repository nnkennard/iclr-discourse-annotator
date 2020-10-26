import json

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import AlignmentAnnotation, AnnotatedPair, Text
from .forms import AnnotationForm

def index(request):
    pair_list = AnnotatedPair.objects.all()
    examples = []
    for obj in pair_list:
        temp = dict(obj.__dict__)
        del temp["_state"]
        print(AlignmentAnnotation.objects.all())
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
            "rebuttal": rebuttal}
    template = loader.get_template('fine_align/detail.html')
    return HttpResponse(template.render(context, request))


