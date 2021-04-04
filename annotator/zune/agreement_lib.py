import collections
import json
from .models import *

def agreement_calculation():
  ann_counter = collections.defaultdict(set)
  review_annotations = ReviewAnnotation.objects.all()
  for r in review_annotations:
      ann_counter[r.review_id].update([r.initials])

  label_list = collections.defaultdict(list)
  for r_id, annotators in ann_counter.items():
      if len(annotators) > 1:
        assert len(annotators) == 2
        for a in sorted(annotators)[:2]:
          for sent_i in range(3):
            label_list[(r_id, sent_i)].append(ReviewSentenceAnnotation.objects.filter(review_id=r_id,
              initials=a, review_sentence_index=sent_i).order_by("-id")[0].labels)
  return arg_agreement(label_list)
 

def arg_agreement(label_list):
    result = {}
    agreement_counts = collections.defaultdict(dict)
    for (r_id, sent_i), values in label_list.items():
        top_maps = [json.loads(z)[0] for z in values]
        assert len(values) == 2
        print(top_maps)
        value = int(top_maps[0]["arg"] == top_maps[1]["arg"])
        agreement_counts[r_id][sent_i] = value
    for r_id, value_map in agreement_counts.items():
        result[r_id] = sum(value_map)/len(value_map)
    return result
        
