# Generated by Django 4.2.17 on 2025-01-05 13:59

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("file", models.FileField(upload_to="documents/")),
                (
                    "media_type",
                    models.CharField(
                        blank=True,
                        choices=[("image", "Image"), ("pdf", "PDF")],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
