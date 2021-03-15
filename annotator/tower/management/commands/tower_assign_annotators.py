from django.core.management.base import BaseCommand
from tower.models import *

import json
import random
from tqdm import tqdm

random.seed(43)

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def add_arguments(self, parser):
        parser.add_argument('annotator_file', type=str)

    def _load_data(self, input_file):
        annotators = []
        with open(input_file, 'r') as f:
            for line in f:
                if 'Name' in line and 'Initials' in line:
                    continue
                annotators.append(line.strip().split())
        return annotators


    def handle(self, *args, **options):

        result = input(
        ("Are you sure you want to delete all annotator "
         "assignments and repopulate the database? Y/N >"))
        if not result == "Y":
            return

        Annotator.objects.all().delete()
        annotators = self._load_data(options["annotator_file"])
        for name, initials in annotators:
            new_annotator = Annotator(name=name, initials=initials)
            new_annotator.save()

        AnnotatorAssignment.objects.all().delete()

        examples = list(sorted(set([(x.dataset, x.example_index)
                for x in Example.objects.all()])))

        annotator_pairs = []
        for i, (_, ann1) in enumerate(annotators):
            for (_, ann2) in annotators[i+1:]:
                annotator_pairs.append((ann1, ann2))

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
                assignment.save()

