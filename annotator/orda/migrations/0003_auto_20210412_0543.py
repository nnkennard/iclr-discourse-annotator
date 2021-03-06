# Generated by Django 3.0.8 on 2021-04-12 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orda', '0002_auto_20210412_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotatorassignment',
            name='is_review_complete',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotatorassignment',
            name='is_review_valid',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotatorassignment',
            name='num_completed_sentences',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotatorassignment',
            name='num_rebuttal_sentences',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
