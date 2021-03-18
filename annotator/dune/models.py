from django.db import models


# Data models

class Example(models.Model):
    class Meta:
        app_label = "dune"

    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()

    forum_id = models.CharField(max_length=30)
    review_id = models.CharField(max_length=30)
    rebuttal_id = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)
    interleaved_index = models.IntegerField()

    rebuttal_sentence_index = models.IntegerField()


class Sentence(models.Model):
    class Meta:
        app_label = "dune"

    comment_id = models.CharField(max_length=30)
    sentence_idx = models.IntegerField()
    text = models.CharField(max_length=1000)
    suffix = models.CharField(max_length=10)

# Annotator models

class Annotator(models.Model):
    class Meta:
        app_label = "dune"
        
    initials = models.CharField(max_length=4)
    name = models.CharField(max_length=50)


class AnnotatorAssignment(models.Model):
    class Meta:
        app_label = "dune"

    annotator_initials = models.CharField(max_length=4)
    rebuttal_id = models.CharField(max_length=30)

# Annotation models

class AlignmentAnnotation(models.Model):
    class Meta:
        app_label = "dune"

    rebuttal_id = models.CharField(max_length=30)
    rebuttal_sentence_index = models.IntegerField()
    annotator_initials = models.CharField(max_length=4)

    is_valid = models.BooleanField()
    
    aligned_review_sentences = models.CharField(max_length=50)
    relation_label = models.CharField(max_length=50)
    comment = models.CharField(max_length=200)
    alignment_errors = models.CharField(max_length=200)

    time_to_annotate = models.IntegerField()


class AlignmentPairAnnotation(models.Model):
    class Meta:
        app_label = "dune"

    rebuttal_id = models.CharField(max_length=30)
    annotator_initials = models.CharField(max_length=4)
    comment = models.CharField(max_length=200)
