import collections
import json
import yaml
from sklearn.metrics import cohen_kappa_score

from .models import *

def get_labels():
  with open("zune/zune_data/labels.yaml", 'r') as f:
    return yaml.safe_load(f)

LABELS = get_labels()

def agreement_calculation():
  ann_counter = collections.defaultdict(set)
  review_annotations = ReviewAnnotation.objects.all()
  for r in review_annotations:
      ann_counter[r.review_id].update([r.initials])

  label_list = collections.defaultdict(list)
  agreers = collections.defaultdict(set)
  for r_id, annotators in ann_counter.items():
      if len(annotators) > 1:
        #assert len(annotators) == 2
        for a in sorted(annotators)[:2]:
          for sent_i in range(3):
            label_list[(r_id, sent_i)].append(
                    ReviewSentenceAnnotation.objects.filter(review_id=r_id,
                    initials=a, review_sentence_index=sent_i).order_by(
                        "-id")[0].labels)
            agreers[r_id].update([a])
  return arg_agreement(label_list), agreers
 
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
        labels1, labels2 = [json.loads(z)[0] for z in values[:2]]
        value_builder_1.append(labels1.get(key, "None"))
        value_builder_2.append(labels2.get(key, "None"))
      kappas[key] = cohen_kappa_score(value_builder_1, value_builder_2)
    return kappas
      
        

