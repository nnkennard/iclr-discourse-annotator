from django.core.management.base import BaseCommand
from fine_align.models import *

import json
from tqdm import tqdm

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def _load_data(self, input_file):
        with open(input_file, 'r') as f:
            return json.loads(f.read())

    def handle(self, *args, **options):
        json_obj = self._load_data(options["input_file"])

        Text.objects.all().delete()

        for text_row in tqdm(json_obj["tokens"]):
            textnode = Text(
                    comment_supernote=text_row["comment_supernote"],
                    chunk_idx=int(text_row["chunk_idx"]),
                    sentence_idx=int(text_row["sentence_idx"]),
                    token_idx=int(text_row["token_idx"]),
                    token=text_row["token"],
                    )
            textnode.save()

        AnnotatedPair.objects.all().delete()
        AlignmentAnnotation.objects.all().delete()

        for node in json_obj["meta"]:
            rebuttal_chunk_maps = Text.objects.values(
                "chunk_idx").filter(
                comment_supernote=node["rebuttal"]).distinct()
            num_rebuttal_chunks = max(x["chunk_idx"] for x in rebuttal_chunk_maps) + 1
            annotated_pair = AnnotatedPair(
                review_supernote = node["review"],
                rebuttal_supernote = node["rebuttal"],
                title=node["title"],
                reviewer="Gotta get authors"
                    )
            annotated_pair.save()        
