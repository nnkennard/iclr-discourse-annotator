from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Annotator(models.Model):
    class Meta:
        app_label = "review_quality"
    name = models.CharField(max_length=50)
    initials = models.CharField(max_length=4)

class Sentence(models.Model):
    class Meta:
        app_label = "review_quality"
    dataset = models.CharField(max_length=30)
    comment_sid = models.CharField(max_length=30)
    sentence_idx = models.IntegerField()
    text = models.CharField(max_length=1000)
    suffix = models.CharField(max_length=10)
 
class CommentPair(models.Model):
    class Meta:
        app_label = "review_quality"
    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()

    forum_id = models.CharField(max_length=30)
    review_sid = models.CharField(max_length=30)
    rebuttal_sid = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)


class AnnotatorAssignment(models.Model):
    class Meta:
        app_label = "review_quality"
    annotator_initials = models.CharField(max_length=4)
    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()


def get_likert_field():
    return models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)])


class Annotation(models.Model): 
    class Meta:
        app_label = "review_quality"
    importance = get_likert_field()
    originality = get_likert_field()
    method = get_likert_field()
    presentation = get_likert_field()
    constructiveness = get_likert_field()
    evidence = get_likert_field()
    interpretation = get_likert_field()
    reproducibility = get_likert_field()
    overall = get_likert_field()
    meta_review = models.CharField(max_length=30)

    comment = models.CharField(max_length=500)
    annotator_initials = models.CharField(max_length=4)
    review_sid = models.CharField(max_length=30)
