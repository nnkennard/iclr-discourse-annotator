from django.core.management.base import BaseCommand
from harbor.models import *

import json
from tqdm import tqdm

CHUNK_LEN = 1000
def create_chunks(text):
    return [text[i:i+CHUNK_LEN] for i in range(0, len(text), CHUNK_LEN)]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'Given a json file, update database for alignments'

    def add_arguments(self, parser):
        parser.add_argument('review_file', type=str)
        parser.add_argument('conference', type=str)

    def _load_data(self, input_file):
        with open(input_file, 'r') as f:
            return json.loads(f.read())

    def handle(self, *args, **options):

        result = input("Are you sure you want to delete all reviews and repopulate the database? Y/N >")
        if not result == "Y":
            return

        json_obj = self._load_data(options["review_file"])
        for pair in tqdm(json_obj["review_rebuttal_pairs"]):
            title = pair["title"]
            if title is None:
                title = "No title"
            if 'forum_url' in pair:
                forum_link = pair["forum_url"]
            else:
                forum_link = ""
            review=Review(
                conference=options["conference"],
                review_id=pair["review_sid"],
                reviewer=pair["review_author"],
                forum=pair["forum"],
                forum_url=forum_link,
                title=title,
            )
            review.save()

            for i, chunk_text in enumerate(create_chunks(
                pair["review_text"]["text"])):
                chunk = Chunk(
                        review_id=pair["review_sid"],
                        chunk_index=i,
                        text=chunk_text)
                chunk.save()
