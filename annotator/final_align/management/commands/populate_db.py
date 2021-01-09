from django.core.management.base import BaseCommand
from final_align.models import *

import json
from tqdm import tqdm

DATASETS = ["truetest", "traindev_test", "traindev_train",
            "traindev_dev"]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def add_arguments(self, parser):
        parser.add_argument('input_dir', type=str)

    def _load_data(self, input_file):
        with open(input_file, 'r') as f:
            return json.loads(f.read())

    def handle(self, *args, **options):

        result = input("Are you sure you want to delete all objects and repopulate the database? Y/N >")
        if not result == "Y":
            return

        AnnotatedPair.objects.all().delete()
        AlignmentAnnotation.objects.all().delete()
        Text.objects.all().delete()
        for dataset in DATASETS:
            json_obj = self._load_data("".join([options["input_dir"], "/",
                dataset, ".json"]))
            print("Entering dataset ", dataset)
            for pair in tqdm(json_obj["review_rebuttal_pairs"][:30]):
                annotated_pair=AnnotatedPair(
                    example_index=pair["index"],
                    dataset=dataset,
                    review_sid=pair["review_sid"],
                    rebuttal_sid=pair["rebuttal_sid"],
                    title=pair["title"],
                    reviewer=pair["review_author"]
                )
                annotated_pair.save()
             
                for text, sid  in [
                        (pair["review_text"], pair["review_sid"]),
                        (pair["rebuttal_text"], pair["rebuttal_sid"])]:
                    for chunk_i, chunk in enumerate(text):
                        for sentence_i, sentence in enumerate(chunk):
                            for token_i, token in enumerate(sentence):
                                textnode = Text(
                                                dataset=dataset,
                                                comment_sid=sid,
                                                chunk_idx=chunk_i,
                                                sentence_idx=sentence_i,
                                                token_idx=token_i,
                                                token=token,)
                                textnode.save()

