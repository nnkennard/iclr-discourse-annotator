from django.core.management.base import BaseCommand
from dune.models import *

import json
from tqdm import tqdm

DATASETS = ["traindev_train", "traindev_dev", "traindev_test", "truetest"]


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def add_arguments(self, parser):
        parser.add_argument('review_dir', type=str)

    def _load_data(self, input_file):
        with open(input_file, 'r') as f:
            return json.loads(f.read())

    def handle(self, *args, **options):
        
        result = input("Are you sure you want to delete all reviews and repopulate the database? Y/N >")
        if not result == "Y":
            return

        Example.objects.all().delete()
        Sentence.objects.all().delete()

        with open(options["review_dir"] + "/interleaved.json", 'r') as f:
            interleaved_list = json.load(f)["interleaved_forum_ids"]

        for dataset in DATASETS:
            input_file = "".join([
                options["review_dir"], "/", dataset, ".json"])
            json_obj = self._load_data(input_file)
            for pair in tqdm(json_obj["review_rebuttal_pairs"]):
                interleaved_index = interleaved_list.index(
                        pair["forum"])
                for i in range(len(pair["rebuttal_text"]["sentences"])):
                    example=Example(
                        dataset=dataset,
                        example_index=pair["index"],
                        forum_id=pair["forum"],
                        review_id=pair["review_sid"],
                        rebuttal_id=pair["rebuttal_sid"],
                        title=pair["title"],
                        reviewer=pair["review_author"],
                        rebuttal_sentence_index=i,
                        interleaved_index=interleaved_index,
                    )
                    example.save()

                for review_or_rebuttal in "review rebuttal".split():
                    text = pair[review_or_rebuttal+"_text"]["text"]
                    for i, sentence_info in enumerate(
                            pair[review_or_rebuttal+"_text"]["sentences"]):
                        sentence_text = text[
                                sentence_info[
                                    "start_index"]:sentence_info["end_index"]]
                        sentence = Sentence(
                                comment_id=pair[review_or_rebuttal+"_sid"],
                                sentence_idx=i,
                                text=sentence_text,
                                suffix=sentence_info["suffix"])
                        sentence.save()
