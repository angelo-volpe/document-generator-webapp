# Generated by Django 5.1.2 on 2024-11-22 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("documentapp", "0007_rename_boxcoordinate_box"),
    ]

    operations = [
        migrations.RenameField(
            model_name="box",
            old_name="x1",
            new_name="end_x",
        ),
        migrations.RenameField(
            model_name="box",
            old_name="x2",
            new_name="end_y",
        ),
        migrations.RenameField(
            model_name="box",
            old_name="y1",
            new_name="start_x",
        ),
        migrations.RenameField(
            model_name="box",
            old_name="y2",
            new_name="start_y",
        ),
    ]
