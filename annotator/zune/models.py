from django.db import models

# ===== Example models

class Example(models.Model):
    class Meta:
        app_label = "zune"

    dataset = models.CharField(max_length=30)
    example_index = models.IntegerField()

    forum_id = models.CharField(max_length=30)
    review_id = models.CharField(max_length=30)
    rebuttal_id = models.CharField(max_length=30)
    title = models.CharField(max_length=300)
    reviewer = models.CharField(max_length=30)
    interleaved_index = models.IntegerField()

    num_rebuttal_sentences = models.IntegerField()


class Sentence(models.Model):
    class Meta:
        app_label = "zune"

    comment_id = models.CharField(max_length=30)
    sentence_idx = models.IntegerField()
    text = models.CharField(max_length=1000)
    suffix = models.CharField(max_length=10)

# ===== Annotation models    

class RebuttalSentenceAnnotation(models.Model):
    class Meta:
        app_label = "zune"

    rebuttal_id = models.CharField(max_length=30)
    rebuttal_sentence_index = models.IntegerField()
    initials = models.CharField(max_length=4)

    is_valid = models.BooleanField()
    
    aligned_review_sentences = models.CharField(max_length=50)
    relation_label = models.CharField(max_length=50)
    comment = models.CharField(max_length=200)
    alignment_errors = models.CharField(max_length=200)

    time_to_annotate = models.IntegerField()
    start_time = models.IntegerField()


class ReviewAnnotation(models.Model):
    class Meta:
        app_label = "zune"

    review_id = models.CharField(max_length=30)
    overall_comment = models.CharField(max_length=30)
    is_valid = models.BooleanField()
    errors = models.CharField(max_length=200)
    initials = models.CharField(max_length=4)

    time_to_annotate = models.IntegerField()
    start_time = models.IntegerField()


class ReviewSentenceAnnotation(models.Model):
    class Meta:
        app_label = "zune"

    review_id = models.CharField(max_length=30)
    review_sentence_index = models.IntegerField()
    initials = models.CharField(max_length=4)
    labels = models.CharField(max_length=200)

# ===== Annotator models

class Annotator(models.Model):
    class Meta:
        app_label = "zune"
        
    initials = models.CharField(max_length=4)
    name = models.CharField(max_length=50)


class AnnotatorAssignment(models.Model):
    class Meta:
        app_label = "zune"

    initials = models.CharField(max_length=4)
    review_id = models.CharField(max_length=30)
    rebuttal_id = models.CharField(max_length=30)
