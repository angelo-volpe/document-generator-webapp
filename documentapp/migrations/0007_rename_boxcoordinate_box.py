# Generated by Django 5.1.2 on 2024-11-22 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "documentapp",
            "0006_boxcoordinate_is_alphabetic_boxcoordinate_is_numeric_and_more",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="BoxCoordinate",
            new_name="Box",
        ),
    ]
