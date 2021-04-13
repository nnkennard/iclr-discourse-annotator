from .models import *

import collections
import yaml


def format_labels():
  with open("orda/orda_data/labels.yaml", 'r') as f:
    LABELS = yaml.safe_load(f)
  label_map = collections.defaultdict(list)

  for obj in LABELS["review_categories"]:
    label_map[obj["short"]] = ["-- " + obj["name"]] + obj["subcategories"]

  allowed_menus = collections.defaultdict(dict)
  for obj in LABELS["allowed_menus"]:
    if obj["allowed"] is not None:
      allowed_menus[obj["name"]]["allowed"] = obj["allowed"]
    else:
      allowed_menus[obj["name"]]["allowed"] = []
    if obj["required"] is not None:
      allowed_menus[obj["name"]]["required"] = obj["required"]
    else:
      allowed_menus[obj["name"]]["required"] = []

  rebuttal_relation_map = collections.defaultdict(list)
  for obj in LABELS["rebuttal_relations"]:
    rebuttal_relation_map[obj["category"]].append((obj["key"], obj["description"]))
    
  rebuttal_relations = []
  for category in "Accept Reject Maybe-arg Non-arg Error".split():
    rebuttal_relations.append((category, rebuttal_relation_map[category]))

  return label_map, allowed_menus, rebuttal_relations


FORMATTED_LABELS, ALLOWED_MENUS, REBUTTAL_RELATIONS = format_labels()


def get_latest_review_annotation(assignment):

  ReviewAnnotation.objects.filter(
      review_id=assignment.example.review_id, initials=assignment.initials).order_by(
          "id")  # This needs to be related to time of sbmission argh

def get_latest_rebuttal_annotation():

    num_completed = len(set(x["rebuttal_sentence_index"]
                      for x in RebuttalSentenceAnnotation.objects.filter(
      rebuttal_id=assignment.rebuttal_id,
      initials=assignment.initials).order_by("id").values(
          "rebuttal_sentence_index")))

def make_presentation_example(assignment):
  return {
      "reviewer":
          assignment.example.reviewer,
      "review_status":
          assignment.is_review_complete,
      "rebuttal_status":
          " / ".join([
              str(assignment.num_completed_sentences),
              str(assignment.num_rebuttal_sentences),
          ]),
      "title":
          assignment.example.title,
      "rebuttal_id":
          assignment.example.rebuttal_id,
      "review_id":
          assignment.example.review_id,
  }


def get_this_annotator_assignments(initials, batch_size=30):
  # Get all assignments
  # Separate completed assignments over 24 hours ago (Add to count)

  all_assignments = AnnotatorAssignment.objects.filter(
          initials=initials).order_by("id")
  assignments_to_show = []
  incomplete_counter = 0
  previously_completed_counter = 0
  for a in all_assignments:
    if a.num_rebuttal_sentences > a.num_completed_sentences:
      incomplete_counter += 1
      assignments_to_show.append(a)
    else:
      assert a.num_completed_sentences == a.num_rebuttal_sentences
      if False: # Actually, if completed over 24 hours ago
        previously_completed_counter += 1
      else:
        assignments_to_show.append(a)
    if incomplete_counter == batch_size:
      break

  return previously_completed_counter, assignments_to_show


def get_htmlified_sentences(supernote_id):
  sentences = Sentence.objects.filter(comment_id=supernote_id)
  final_sentences = []
  for i, sentence in enumerate(sentences):
    final_sentences.append({"text": sentence.text + sentence.suffix, "idx": i})
  return final_sentences
