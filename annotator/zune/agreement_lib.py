import collections
import json
import yaml
from sklearn.metrics import cohen_kappa_score

from .models import *

def get_labels():
  with open("zune/zune_data/labels.yaml", 'r') as f:
    return yaml.safe_load(f)

LABELS = get_labels()


def review_label_agreement():
  ann_counter = collections.defaultdict(set)
  review_annotations = ReviewAnnotation.objects.all()
  for r in review_annotations:
      ann_counter[r.review_id].update([r.initials])

  label_list = collections.defaultdict(list)
  agreers = collections.defaultdict(set)
  for r_id, annotators in ann_counter.items():
      if len(annotators) > 1:
        for a in sorted(annotators)[:2]:
          for sent_i in range(3):
            label_list[(r_id, sent_i)].append(
                    ReviewSentenceAnnotation.objects.filter(review_id=r_id,
                    initials=a, review_sentence_index=sent_i).order_by(
                        "-id")[0].labels)
            agreers[r_id].update([a])
  return label_list, agreers

def get_rebuttal_label(rebuttal_id, rebuttal_sentence_index, annotator):
    return get_latest_annotation(rebuttal_id, rebuttal_sentence_index,
            annotator).relation_label

def get_latest_annotation(rebuttal_id, rebuttal_sentence_index, annotator):
    return RebuttalSentenceAnnotation.objects.filter(
          rebuttal_id=rebuttal_id,
          rebuttal_sentence_index=rebuttal_sentence_index,
          initials=annotator).order_by("-id")[0]

def get_rebuttal_annotation_pairs():
  rebuttal_annotations = RebuttalSentenceAnnotation.objects.values(
          "rebuttal_id", "rebuttal_sentence_index", "initials").distinct()
  pairs_to_consider = collections.defaultdict(list)
  for obj in rebuttal_annotations:
      pairs_to_consider[(obj["rebuttal_id"],
          obj["rebuttal_sentence_index"])].append(obj["initials"])
  return pairs_to_consider

def rebuttal_label_agreement():
  pairs_to_consider = get_rebuttal_annotation_pairs()
  values_1, values_2 = [], []
  for (reb_id, idx), annotators in pairs_to_consider.items():
      if len(annotators) < 2:
          continue
      else:
          anns = annotators[:2]
      values_1.append(get_rebuttal_label(reb_id, idx, anns[0]))
      values_2.append(get_rebuttal_label(reb_id, idx, anns[1]))
  return cohen_kappa_score(values_1, values_2)

def get_label_list(reb_id, idx, annotator):
    return get_latest_annotation(reb_id, idx,
            annotator).aligned_review_sentences().split("|")

def jaccard(l1, l2):
    if not l1 and not l2:
        return 0.0
    s1 = set(l1)
    s2 = set(l2)
    return len(s1.intersection(s2))/len(s1.union(s2))

def get_jaccard():
    pairs_to_consider = get_rebuttal_annotation_pairs()
    jaccard_list = []
    for (reb_id, idx), annotators in pairs_to_consider.items():
      if len(annotators) < 2:
          continue
      else:
          anns = annotators[:2]
          jaccard_list.append(jaccard(
              get_label_list(reb_id, idx, anns[0]),
              get_label_list(reb_id, idx, anns[1]),
              ))
    return maybe_avg(jaccard_list)

def agreement_calculation():
    review_label_list, agreers = review_label_agreement()
    rebuttal_label_kappa = rebuttal_label_agreement()
    rebuttal_link_agreement_val = get_jaccard()

    return (arg_agreement(review_label_list), agreers, rebuttal_label_kappa,
            rebuttal_link_agreement_val)
 
def get_both_have(dict1, dict2, key):
    if key in dict1:
        return int(key in dict2)
    else:
        return int(key not in dict2)
 
def maybe_avg(l):
    if not l:
        return None
    else:
        return sum(l) / len(l)

def arg_agreement(label_list):
    keys = [x["short"] for x in LABELS["review_categories"]]
    agreement_counts = collections.defaultdict(dict)
    kappas = {}
    for key in keys:
      value_builder_1, value_builder_2 = [], []
      for (r_id, sent_i), values in label_list.items():
        labels1, labels2 = [json.loads(z)[0] for z in values]
        value_builder_1.append(labels1.get(key, "None"))
        value_builder_2.append(labels2.get(key, "None"))
      kappas[key] = cohen_kappa_score(value_builder_1, value_builder_2)
    return kappas
      
