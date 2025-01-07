import io
from pathlib import Path

import filetype
from drf_extra_fields.fields import Base64FileField
from PIL import Image as PilImage
from pypdf import PdfReader
from rest_framework import serializers

from .models import Document


class Base64FileFieldSerializer(Base64FileField):
    """
    A custom serializer field to handle base64-encoded files.
    """

    ALLOWED_MIME_TYPES = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "application/pdf": "pdf",
    }

    ALLOWED_TYPES = ["pdf", "jpg", "jpeg", "png", "gif", "webp"]

    def get_file_extension(self, filename, decoded_file):
        extension = filetype.guess_extension(decoded_file)
        return extension

    def to_internal_value(self, data):
        if isinstance(data, str):
            return super().to_internal_value(data)
        return data


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for images/pdfs documents.
    """

    location = serializers.CharField(source="file.url")

    class Meta:
        model = Document
        fields = ["id", "media_type", "location", "uploaded_at"]


class DocumentListSerializer(serializers.Serializer):
    """
    Serializer for handling multiple document uploads.
    """

    file = Base64FileFieldSerializer(required=True)

    def create(self, validated_data):
        """
        Override the create method to save media_type along with files.
        """
        file = validated_data.get("file")
        if not file:
            raise serializers.ValidationError("Please upload a valid file.")

        extension = Path(file.name).suffix.lower().lstrip(".")
        if extension in ["jpg", "jpeg", "png", "gif", "webp"]:
            media_type = "image"
        elif extension == "pdf":
            media_type = "pdf"
        else:
            raise serializers.ValidationError(f"Unsupported file type: {extension}")

        document = Document(file=file, media_type=media_type)
        return document

    class Meta:
        list_serializer_class = serializers.ListSerializer


class ImageSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source="file.url")
    width = serializers.IntegerField(read_only=True)
    height = serializers.IntegerField(read_only=True)
    num_pages = serializers.IntegerField(read_only=True)
    page_width = serializers.IntegerField(read_only=True)
    page_height = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "location",
            "media_type",
            "width",
            "height",
            "num_pages",
            "page_width",
            "page_height",
            "uploaded_at",
        ]

    def to_representation(self, instance):
        """
        Customize the response depending on the file type (image or PDF).
        """
        data = super().to_representation(instance)
        image = PilImage.open(instance.file)
        data["width"], data["height"] = image.size
        data["channels"] = len(image.getbands())
        return data


class PdfSerializer(serializers.ModelSerializer):
    """
    Serializer for representing PDF documents and their metadata.
    """

    location = serializers.CharField(source="file.url")
    num_pages = serializers.IntegerField(read_only=True)
    page_dimensions = serializers.ListField(
        child=serializers.DictField(), read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "location",
            "num_pages",
            "page_dimensions",
            "uploaded_at",
        ]

    def to_representation(self, instance):
        """
        Customize the response depending on the file type (image or PDF).
        """
        data = super().to_representation(instance)
        pdf_file = instance.file.read()
        pdf_reader = PdfReader(io.BytesIO(pdf_file))
        data["num_pages"] = len(pdf_reader.pages)

        page_dimensions = []
        for page in pdf_reader.pages:
            page_dimensions.append(
                {
                    "width": page.mediabox.width,
                    "height": page.mediabox.height,
                }
            )

        data["page_dimensions"] = page_dimensions
        return data


class RotateImageSerializer(serializers.Serializer):
    """
    Serializer to validate and process the data for rotating an image document.
    """

    id = serializers.UUIDField(required=True)
    rotation_angle = serializers.FloatField(required=True)


class ConvertPdfToImageSerializer(serializers.Serializer):
    """
    Serializer to validate and process the data for converting a PDF document to an image.
    """

    id = serializers.UUIDField(required=True)
