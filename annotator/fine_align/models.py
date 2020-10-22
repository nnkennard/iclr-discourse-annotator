from django.db import models

# Create your models here.

class AlignmentAnnotation(models.Model):
    class Meta:
        app_label = "fine_align"
    review_supernote = models.CharField(max_length=30)
    rebuttal_supernote = models.CharField(max_length=30)
    
    rebuttal_chunk = models.IntegerField()
    review_start_idx = models.IntegerField()
    review_exclusive_end_idx = models.IntegerField()

    error = models.IntegerField()
    comment = models.CharField(max_length=200)
    annotator = models.CharField(max_length=30)


class AnnotatedPair(models.Model):
    class Meta:
        app_label = "fine_align"
    review_supernote = models.CharField(max_length=30)
    rebuttal_supernote = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)

class Text(models.Model):
    class Meta:
        app_label = "fine_align"
    comment_supernote = models.CharField(max_length=30)
    chunk_idx = models.IntegerField()
    sentence_idx = models.IntegerField()
    token_idx = models.IntegerField()
    token = models.CharField(max_length=30)
    
