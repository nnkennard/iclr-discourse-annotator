# Generated by Django 3.0.8 on 2021-03-08 23:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importance', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('originality', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('strengths_weaknesses', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('useful_comments', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('constructive', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('evidence', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('interpretation', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('overall', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('comment', models.CharField(max_length=500)),
                ('annotator_initials', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Annotator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('initials', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='AnnotatorAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotator_initials', models.CharField(max_length=4)),
                ('dataset', models.CharField(max_length=30)),
                ('example_index', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CommentPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.CharField(max_length=30)),
                ('example_index', models.IntegerField()),
                ('forum_id', models.CharField(max_length=30)),
                ('review_sid', models.CharField(max_length=30)),
                ('rebuttal_sid', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=300)),
                ('reviewer', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.CharField(max_length=30)),
                ('comment_sid', models.CharField(max_length=30)),
                ('sentence_idx', models.IntegerField()),
                ('text', models.CharField(max_length=1000)),
                ('suffix', models.CharField(max_length=10)),
            ],
        ),
    ]