from django.core.management.base import BaseCommand
from tower.models import Sentence, Example

import json
from tqdm import tqdm

DATASETS = [
        #"truetest", "traindev_test", 
        "traindev_train",
        #"traindev_dev"
        ]

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

        Example.objects.all().delete()
        Sentence.objects.all().delete()
        for dataset in DATASETS:
            json_obj = self._load_data("".join([options["input_dir"], "/",
                dataset, ".json"]))
            for pair in tqdm(json_obj["review_rebuttal_pairs"]):
                num_sentences = len(pair["review_text"]["sentences"])
                for rebuttal_index in range(num_sentences):
                    example=Example(
                        example_index=pair["index"],
                        forum_id=pair["forum"],
                        dataset=dataset,
                        review_sid=pair["review_sid"],
                        rebuttal_sid=pair["rebuttal_sid"],
                        title=pair["title"],
                        reviewer=pair["review_author"],
                        rebuttal_index=rebuttal_index,
                    )
                    example.save()
             
                for text_obj, sid  in [
                        (pair["review_text"], pair["review_sid"]),
                        (pair["rebuttal_text"], pair["rebuttal_sid"])]:
                    for sentence_i, sentence in enumerate(text_obj["sentences"]):
                        text = text_obj[
                            "text"][
                            sentence["start_index"]:sentence["end_index"]]
                        sentence_node = Sentence(
                                        comment_sid=sid,
                                        sentence_idx=sentence_i,
                                        text=text,
                                        suffix=sentence["suffix"]
                                        )
                        sentence_node.save()

