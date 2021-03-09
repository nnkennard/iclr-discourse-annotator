# Generated by Django 3.0.8 on 2021-03-07 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
            name='CommentAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_sid', models.CharField(max_length=30)),
                ('rebuttal_sid', models.CharField(max_length=30)),
                ('error', models.CharField(max_length=200)),
                ('comment', models.CharField(max_length=200)),
                ('annotator', models.CharField(max_length=30)),
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
        migrations.CreateModel(
            name='SentenceAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_sid', models.CharField(max_length=30)),
                ('rebuttal_sid', models.CharField(max_length=30)),
                ('annotator_initials', models.CharField(max_length=4)),
                ('rebuttal_sentence_idx', models.IntegerField()),
                ('aligned_review_sentences', models.CharField(max_length=50)),
                ('alignment_comment', models.CharField(max_length=200)),
                ('alignment_errors', models.CharField(max_length=200)),
                ('relation', models.CharField(max_length=150)),
                ('relation_comment', models.CharField(max_length=200)),
                ('relation_errors', models.CharField(max_length=200)),
            ],
        ),
    ]