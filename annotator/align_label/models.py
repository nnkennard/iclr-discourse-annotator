from django.db import models


class Sentence(models.Model):
    class Meta:
        app_label = "align_label"
    dataset = models.CharField(max_length=30)
    comment_sid = models.CharField(max_length=30)
    sentence_idx = models.IntegerField()
    text = models.CharField(max_length=1000)
    suffix = models.CharField(max_length=10)
    

class Annotator(models.Model):
    class Meta:
        app_label = "align_label"
    name = models.CharField(max_length=50)
    initials = models.CharField(max_length=4)



class AnnotatorAssignment(models.Model):
    class Meta:
        app_label = "align_label"
    annotator_initials = models.CharField(max_length=4)
    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()


class CommentPair(models.Model):
    class Meta:
        app_label = "align_label"
    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()

    forum_id = models.CharField(max_length=30)
    review_sid = models.CharField(max_length=30)
    rebuttal_sid = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)


class SentenceAnnotation(models.Model):
    class Meta:
        app_label = "align_label"

    review_sid = models.CharField(max_length=30)
    rebuttal_sid = models.CharField(max_length=30)
    annotator_initials = models.CharField(max_length=4)
    
    rebuttal_sentence_idx = models.IntegerField()
    aligned_review_sentences = models.CharField(max_length=50)
    alignment_comment = models.CharField(max_length=200)
    alignment_errors =  models.CharField(max_length=200)

    relation = models.CharField(max_length=150)
    relation_comment = models.CharField(max_length=200)
    relation_errors =  models.CharField(max_length=200)


class CommentAnnotation(models.Model):
    class Meta:
        app_label = "align_label"
        
    review_sid = models.CharField(max_length=30)
    rebuttal_sid = models.CharField(max_length=30)

    error = models.CharField(max_length=200)
    comment = models.CharField(max_length=200)
    annotator = models.CharField(max_length=30)
