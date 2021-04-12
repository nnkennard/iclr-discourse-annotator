from django.core.management.base import BaseCommand
from zune.models import *

import json
from tqdm import tqdm


def annotator_gen():
    annotators = Annotator.objects.all()
    annotator_pairs = []
    for i, ann1 in enumerate(annotators):
        for ann2 in annotators[i+1:]:
            annotator_pairs.append((ann1.initials, ann2.initials))

    index = 0
    while True:
        yield annotator_pairs[index % len(annotator_pairs)]
        index += 1

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def handle(self, *args, **options):

        result = input(
        ("Are you sure you want to delete all annotator "
         "assignments and repopulate the database? Y/N >"))
        if not result == "Y":
            return

        for annotator in Annotator.objects.all():
            if annotator.initials in "AS CB MC PKY NNK NK PY TJO TO RD".split():
                continue
            for i in range(2):
                examples = Example.objects.filter(interleaved_index=i)
                for example in examples:
                    assignment = AnnotatorAssignment(
                        rebuttal_id=example.rebuttal_id,
                        review_id=example.review_id,
                        initials=annotator.initials)
                    assignment.save()

