from django.db import models

# Create your models here.

class Sentence(models.Model):
    class Meta:
        app_label = "tower"

    comment_sid = models.CharField(max_length=30)
    sentence_idx = models.IntegerField()
    text = models.CharField(max_length=1000)
    suffix = models.CharField(max_length=10)
 

class Annotator(models.Model):
    class Meta:
        app_label = "tower"
        
    initials = models.CharField(max_length=4)
    name = models.CharField(max_length=50)


class AnnotatorAssignment(models.Model):
    class Meta:
        app_label = "tower"

    annotator_initials = models.CharField(max_length=4)
    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()


class Example(models.Model):
    class Meta:
        app_label = "tower"

    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()

    forum_id = models.CharField(max_length=30)
    review_sid = models.CharField(max_length=30)
    rebuttal_sid = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)

    rebuttal_index = models.IntegerField()


class SentenceAnnotation(models.Model):
    class Meta:
        app_label = "tower"

    rebuttal_sid = models.CharField(max_length=30)
    rebuttal_sentence_idx = models.IntegerField()
    annotator_initials = models.CharField(max_length=4)

    is_valid = models.BooleanField()
    
    aligned_review_sentences = models.CharField(max_length=50)
    relation_label = models.CharField(max_length=50)
    comment = models.CharField(max_length=200)
    alignment_errors =  models.CharField(max_length=200)


class PairAnnotation(models.Model):
    class Meta:
        app_label = "tower"

    rebuttal_sid = models.CharField(max_length=30)
    annotator_initials = models.CharField(max_length=4)
    comment = models.CharField(max_length=200)
