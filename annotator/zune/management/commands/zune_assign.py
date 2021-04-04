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

        AnnotatorAssignment.objects.all().delete()

        ann_gen = annotator_gen()

        max_interleaved_index = max(i["interleaved_index"]
            for i in Example.objects.all().values("interleaved_index"))

        for annotator in Annotator.objects.all():
            assignment = AnnotatorAssignment(
                    rebuttal_id="example_rebuttal",
                    review_id="example_review",
                    initials=annotator.initials)
            assignment.save()

            # Janky stuff for pilot
            for i in range(1, max_interleaved_index):
                examples = Example.objects.filter(interleaved_index=i)
                for example in examples:
                    assignment = AnnotatorAssignment(
                        rebuttal_id=example.rebuttal_id,
                        review_id=example.review_id,
                        initials=annotator.initials)
                    assignment.save()

        return



        for i in tqdm(range(1, max_interleaved_index)): # This is picking a forum
            examples = Example.objects.all().filter(interleaved_index=i)
            rebuttal_ids = set([example.rebuttal_id for example in examples])
            
            this_forum_annotators = next(ann_gen)
            if 'NNK' not in this_forum_annotators:
                this_forum_annotators = list(this_forum_annotators) + ["NNK"]

            for rebuttal_id in rebuttal_ids:
                maybe_examples = Example.objects.all().filter(
                            rebuttal_id=rebuttal_id)
                for ann in this_forum_annotators:
                    for example in maybe_examples:
                        assignment = AnnotatorAssignment(
                                rebuttal_id=example.rebuttal_id,
                                review_id=example.review_id,
                                initials=ann
                                )
                        assignment.save()
        
