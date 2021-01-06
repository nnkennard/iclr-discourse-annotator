# Generated by Django 3.0.8 on 2021-01-06 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlignmentAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_sid', models.CharField(max_length=30)),
                ('rebuttal_sid', models.CharField(max_length=30)),
                ('rebuttal_chunk_idx', models.IntegerField()),
                ('review_sentence_idx', models.IntegerField()),
                ('error', models.CharField(max_length=200)),
                ('comment', models.CharField(max_length=200)),
                ('annotator', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='AnnotatedPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_sid', models.CharField(max_length=30)),
                ('rebuttal_sid', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=300)),
                ('reviewer', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_sid', models.CharField(max_length=30)),
                ('chunk_idx', models.IntegerField()),
                ('sentence_idx', models.IntegerField()),
                ('token_idx', models.IntegerField()),
                ('token', models.CharField(max_length=30)),
            ],
        ),
    ]
