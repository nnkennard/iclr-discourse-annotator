from django.core.management.base import BaseCommand
from final_align.models import *

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

        AnnotatedPair.objects.all().delete()
        AlignmentAnnotation.objects.all().delete()
        Text.objects.all().delete()

        for pair in tqdm(json_obj["review_rebuttal_pairs"]):
            annotated_pair=AnnotatedPair(
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
                                            comment_sid=sid,
                                            chunk_idx=chunk_i,
                                            sentence_idx=sentence_i,
                                            token_idx=token_i,
                                            token=token,)
                            textnode.save()

