# Generated by Django 3.0.8 on 2021-03-18 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dune', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotatorAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotator_initials', models.CharField(max_length=4)),
                ('rebuttal_id', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='example',
            name='interleaved_index',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
    ]