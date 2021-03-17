from django.core.management.base import BaseCommand
from harbor.models import *

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

        Assignment.objects.all().delete()
        print(Review.objects.all())
        print(Annotator.objects.all())

        for review in Review.objects.all():
            for annotator in Annotator.objects.all():
                assignment = Assignment(
                        review_id=review.review_id,
                        annotator_initials=annotator.initials
                        )
                assignment.save()
