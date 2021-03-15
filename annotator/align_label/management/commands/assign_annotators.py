from django.core.management.base import BaseCommand
from align_label.models import *

import json
import random
from tqdm import tqdm

random.seed(43)

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def handle(self, *args, **options):

        print("Populating align_label assignments")

        result = input(
        ("Are you sure you want to delete all annotator "
         "assignments and repopulate the database? Y/N >"))
        if not result == "Y":
            return

        AnnotatorAssignment.objects.all().delete()

        annotators = [x.initials for x in Annotator.objects.all()]
        examples = [(x.dataset, x.example_index)
                for x in CommentPair.objects.all()]

        annotator_pairs = []
        for i, ann1 in enumerate(annotators):
            for ann2 in annotators[i+1:]:
                annotator_pairs.append((ann1, ann2))

        print(len(examples), print(len(annotator_pairs)))

        examples_per_pair = int(len(examples) / len(annotator_pairs))
        random.shuffle(examples)

        annotator_pair_map ={}
        for i, annotator_pair in enumerate(annotator_pairs):
            for example in examples[i*examples_per_pair:(i+1)*examples_per_pair]:
                annotator_pair_map[example] = annotator_pair

        for (dataset, example_index), annotators in annotator_pair_map.items():
            for annotator in annotators:
                assignment = AnnotatorAssignment(
                        annotator_initials=annotator,
                        dataset=dataset,
                        example_index=example_index
                        )
                print("saving")
                assignment.save()

