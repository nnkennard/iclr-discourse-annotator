# Generated by Django 3.0.8 on 2021-03-20 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dune', '0002_auto_20210318_1829'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alignmentannotation',
            old_name='annotator_initials',
            new_name='initials',
        ),
        migrations.RenameField(
            model_name='alignmentpairannotation',
            old_name='annotator_initials',
            new_name='initials',
        ),
        migrations.RenameField(
            model_name='annotatorassignment',
            old_name='annotator_initials',
            new_name='initials',
        ),
    ]