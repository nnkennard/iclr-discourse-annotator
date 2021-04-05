from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *
from .forms import AnnotationForm
from .agreement_lib import *

import collections
import json
import yaml


def get_labels():
  with open("zune/zune_data/labels.yaml", 'r') as f:
    return yaml.safe_load(f)


LABELS = get_labels()


def get_htmlified_sentences(supernote_id):
  sentences = Sentence.objects.filter(comment_id=supernote_id)
  final_sentences = []
  for i, sentence in enumerate(sentences):
    final_sentences.append({"text": sentence.text + sentence.suffix, "idx": i})
  return final_sentences


def index(request):
  template = loader.get_template('zune/index.html')
  context = {"annotators": Annotator.objects.all()}
  return HttpResponse(template.render(context, request))


def make_presentation_example(assignment):
  example = Example.objects.get(rebuttal_id=assignment.rebuttal_id)

  review_annotations = ReviewAnnotation.objects.filter(
      review_id=assignment.review_id, initials=assignment.initials).order_by(
          "id")  # This needs to be related to time of sbmission argh
  if not review_annotations:
    review_status = "Not started"
  elif review_annotations[0].is_valid:
    review_status = "Complete"
  else:
    review_status = "Not completed"
  
  num_completed = len(set(x["rebuttal_sentence_index"]
                      for x in RebuttalSentenceAnnotation.objects.filter(
      rebuttal_id=assignment.rebuttal_id,
      initials=assignment.initials).order_by("id").values(
          "rebuttal_sentence_index")))

  return {
      "reviewer":
          example.reviewer,
      "review_status":
          review_status,
      "rebuttal_status":
          " / ".join([
              str(num_completed),
              str(example.num_rebuttal_sentences),
          ]),
      "title":
          example.title,
      "rebuttal_id":
          example.rebuttal_id,
      "review_id":
          example.review_id,
  }


def assignments(request, initials):
  annotator = Annotator.objects.get(initials=initials)
  presentation_examples = [
      make_presentation_example(assignment)
      for assignment in AnnotatorAssignment.objects.filter(
          initials=initials).order_by("id")
  ]
  template = loader.get_template('zune/assignment.html')
  context = {
      "examples": presentation_examples,
      "annotator": {
          "name": annotator.name,
          "initials": annotator.initials
      }
  }
  return HttpResponse(template.render(context, request))

default_labels = {
  
  "top": "Arg type",
  "fine": "Arg subtype",
  "aspect": "Aspect",
  "grounding": "Grounding",
  "polarity": "Polarity"

}

def format_labels():
  label_map = collections.defaultdict(list)
  for obj in LABELS["review_categories"]:
    label_map[obj["short"]] = ["-- " + obj["name"]] + obj["subcategories"]

  label_map["fine"] = sum([["-- Fine"],
                          ["Manuscript:" + x for x in label_map["manu"][1:]],
                          ["Rebuttal:" + x for x in label_map["rebu"][1:]]], [])

  allowed_menus = collections.defaultdict(dict)
  for obj in LABELS["allowed_menus"]:
    allowed_menus[obj["name"]]["allowed"] = obj["allowed"]
    allowed_menus[obj["name"]]["required"] = obj["required"]

  rebuttal_relations = []
  for obj in LABELS["rebuttal_relations"]:
    name = obj["name"]
    for subobj in obj["subcategories"]:
      for subsub in subobj["subcategories"]:
        rebuttal_relations.append((name, subobj["name"], subsub,
          LABELS["rebuttal_relation_descriptions"][subsub]))

  return label_map, allowed_menus, rebuttal_relations


FORMATTED_LABELS, ALLOWED_MENUS, REBUTTAL_RELATIONS = format_labels()


def get_annotation_context(initials, rebuttal_id, review_id, index):
  this_annotator_annotations = [
      x["rebuttal_sentence_index"]
      for x in RebuttalSentenceAnnotation.objects.filter(
          initials=initials, rebuttal_id=rebuttal_id).values(
              "rebuttal_sentence_index")
  ]

  rebuttal_sentences = get_htmlified_sentences(rebuttal_id)
  statuses = [
      i in this_annotator_annotations for i in range(len(rebuttal_sentences))
  ]

  maybe_previous_annotation = RebuttalSentenceAnnotation.objects.filter(
      initials=initials,
      rebuttal_id=rebuttal_id,
      rebuttal_sentence_index=index - 1).order_by("-id")
  if maybe_previous_annotation:
    previous_annotation = maybe_previous_annotation[0].aligned_review_sentences
    previous_label = maybe_previous_annotation[0].relation_label
  else:
    previous_annotation = ""
    previous_label = ""

  review_annotation_map = {}

  for ann in ReviewSentenceAnnotation.objects.filter(
    review_id=review_id, initials=initials).order_by("id"):
    review_annotation_map[ann.review_sentence_index] = json.loads(ann.labels)

  review_annotations = [review_annotation_map[i] for i in range(len(review_annotation_map))]


  return {
      "text": {
          "review_sentences": get_htmlified_sentences(review_id),
          "rebuttal_sentences": rebuttal_sentences,
          "rebuttal_sentence": rebuttal_sentences[index],
      },
      "other_annotations": {
          "statuses": statuses,
          "previous_label": previous_label,
          "previous_alignment": previous_annotation,
          "review_annotations": review_annotations
      }
  }


def annotate_rebuttal(request, rebuttal, initials, index):
  example = Example.objects.get(rebuttal_id=rebuttal)
  context = get_annotation_context(initials, rebuttal, example.review_id, index)
  context.update({
      "alignment_errors": LABELS["alignment_errors"],
      "labels": REBUTTAL_RELATIONS,
      "form": AnnotationForm(),
      "metadata": {
          "paper_title": example.title,
          "initials": initials,
          "reviewer": example.reviewer,
          "forum_id": example.forum_id,
          "rebuttal_id": rebuttal,
          "review_id": example.review_id,
          "rebuttal_index": index
      }
  })
  template = loader.get_template('zune/annotate_rebuttal.html')
  return HttpResponse(template.render(context, request))


def annotate_review(request, review, initials):

  example = Example.objects.get(review_id=review)
  review_sentences = get_htmlified_sentences(review)
  template = loader.get_template('zune/annotate_review.html')
  return HttpResponse(
      template.render(
          {
              "text": {
                  "review_sentences": review_sentences
              },
              "labels": FORMATTED_LABELS,
              "form": AnnotationForm(),
              "menu_map": ALLOWED_MENUS,
              "metadata": {
                  "paper_title": example.title,
                  "initials": initials,
                  "reviewer": example.reviewer,
                  "forum_id": example.forum_id,
                  "review_id": example.review_id
              }
          }, request))


def submitted(request):
  form = AnnotationForm(request.POST)
  if form.is_valid():
    annotation_obj = json.loads(form.cleaned_data["annotation"])
    metadata = annotation_obj["metadata"]

    review_annotation = ReviewAnnotation(
        review_id=metadata["review_id"],
        overall_comment=annotation_obj["comments"],
        is_valid=True,
        initials=metadata["initials"],
        time_to_annotate=annotation_obj["time_to_annotate"],
        start_time=annotation_obj["start_time"],
    )
    review_annotation.save()

    arg_map = collections.defaultdict(list)
    for key in annotation_obj["labels"]:
      sent, arg_no = key.split("-")
      arg_map[int(sent)].append(int(arg_no))


    for sent_index in sorted(arg_map.keys()):
      assert set(arg_map[sent_index]).issubset(set(range(2)))
      label_list = [
        annotation_obj["labels"][str(sent_index) + "-" + str(i)]
        for i in sorted(arg_map[sent_index])
      ]

      sentence_annotation = ReviewSentenceAnnotation(
          review_id=metadata["review_id"],
          review_sentence_index=sent_index,
          initials=metadata["initials"],
          labels=json.dumps(label_list))
      sentence_annotation.save()

    template = loader.get_template('zune/submitted.html')
  return HttpResponse(
      template.render({"initials": annotation_obj["metadata"]["initials"]},
                      request))

def rebuttal_submitted(request):
  form = AnnotationForm(request.POST)
  if form.is_valid():
    annotation_obj = json.loads(form.cleaned_data["annotation"])
    metadata = annotation_obj["metadata"]
    print(annotation_obj["relation_label"])
    annotation = RebuttalSentenceAnnotation(
        rebuttal_id=metadata["rebuttal_id"],
        rebuttal_sentence_index=metadata["rebuttal_index"],
        initials=metadata["initials"],
        is_valid=True,
        aligned_review_sentences="|".join(
          [str(i) for i, j in enumerate(annotation_obj["alignment_labels"]) if j]),
        relation_label=annotation_obj["relation_label"],
        comment=annotation_obj["comments"],
        alignment_errors=annotation_obj["alignment_errors"],
        time_to_annotate=annotation_obj["time_to_annotate"],
        start_time=annotation_obj["start_time"],
    )
    annotation.save()

    maybe_next_index = annotation_obj["metadata"]["rebuttal_index"] + 1
    if (maybe_next_index ==
        annotation_obj["num_rebuttal_sentences"]):
      next_sentence_info = {"valid":False,
                "initials":metadata["initials"]}
    else:
      next_sentence_info = {
                "rebuttal_sentence_index":maybe_next_index,
                "initials":metadata["initials"],
                "rebuttal_id":metadata["rebuttal_id"],
                "valid": True}

    template = loader.get_template('zune/rebuttal_submitted.html')
  return HttpResponse(
      template.render({"initials": annotation_obj["metadata"]["initials"],
          "next_sentence_info":next_sentence_info},
                      request))

def agreement(request):
  label_list = agreement_calculation()
  info = {"baba": label_list}
  template = loader.get_template('zune/agreement.html')
  return HttpResponse(
          template.render({"info":info},
                      request))


