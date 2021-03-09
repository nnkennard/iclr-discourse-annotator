from django.core.management.base import BaseCommand
from review_quality.models import *

import json
import random
from tqdm import tqdm

random.seed(43)

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def handle(self, *args, **options):

        result = input(
        ("Are you sure you want to delete all annotator "
         "assignments and repopulate the database? Y/N >"))
        if not result == "Y":
            return

        AnnotatorAssignment.objects.all().delete()

        annotators = [x.initials for x in Annotator.objects.all()]
        examples = [(x.dataset, x.example_index)
                for x in CommentPair.objects.all()]
        for (dataset, example_index) in examples:
            for annotator in annotators:
                assignment = AnnotatorAssignment(
                        annotator_initials=annotator,
                        dataset=dataset,
                        example_index=example_index
                        )
                assignment.save()

