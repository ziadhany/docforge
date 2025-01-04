import uuid

from django.db import models


class Document(models.Model):
    """
    A model to represent uploaded files.
    """

    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("pdf", "PDF"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="documents/")
    media_type = models.CharField(
        max_length=20, choices=MEDIA_TYPE_CHOICES, blank=True, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
