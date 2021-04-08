from django.db import models


class Annotator(models.Model):
    class Meta:
        app_label = "harbor"

    name = models.CharField(max_length=50)
    initials = models.CharField(max_length=4)


class Chunk(models.Model):
    class Meta:
        app_label = "harbor"

    review_id = models.CharField(max_length=30)
    chunk_index = models.IntegerField()
    text = models.CharField(max_length=1000)


class Review(models.Model):
    class Meta:
        app_label = "harbor"

    conference = models.CharField(max_length=30)
    review_id = models.CharField(max_length=30)
    reviewer = models.CharField(max_length=30)
    forum = models.CharField(max_length=30)
    title = models.CharField(max_length=300)


class Annotation(models.Model):
    class Meta:
        app_label = "harbor"

    review_id = models.CharField(max_length=30)
    annotator_initials = models.CharField(max_length=5)
    ratings = models.CharField(max_length=1000)
    comment = models.CharField(max_length=500)


class Assignment(models.Model):
    class Meta:
        app_label = "harbor"

    review_id = models.CharField(max_length=30)
    annotator_initials = models.CharField(max_length=5)
