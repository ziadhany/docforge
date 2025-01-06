import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from pdf2image import convert_from_path
from PIL import Image
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from docengine.serializer import (
    ConvertPdfToImageSerializer,
    DocumentListSerializer,
    DocumentSerializer,
    ImageSerializer,
    PdfSerializer,
    RotateImageSerializer,
)

from .models import Document


class DocumentUploadView(APIView):
    """
    API endpoint for uploading multiple documents.
    """

    def post(self, request, *args, **kwargs):
        serializer = DocumentListSerializer(data=request.data, many=True)
        if serializer.is_valid():
            documents = serializer.save()

            Document.objects.bulk_create(documents)
            return Response(
                {
                    "message": "Documents uploaded successfully",
                    "documents": [doc.id for doc in documents],
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


class ImageListView(ListAPIView):
    """
    API endpoint for retrieving a list of all uploaded images.
    """

    queryset = Document.objects.filter(media_type="image")
    serializer_class = DocumentSerializer


class PdfListView(ListAPIView):
    """
    API endpoint for retrieving a list of all uploaded PDFs.
    """

    queryset = Document.objects.filter(media_type="pdf")
    serializer_class = DocumentSerializer


class ImageRetrieveDeleteView(RetrieveDestroyAPIView):
    """
    API view to retrieve or delete an image document.
    """

    queryset = Document.objects.filter(media_type="image")
    serializer_class = ImageSerializer
    lookup_field = "id"


class PdfRetrieveDeleteView(RetrieveDestroyAPIView):
    """
    API view to retrieve or delete an pdf document.
    """

    queryset = Document.objects.filter(media_type="pdf")
    serializer_class = PdfSerializer
    lookup_field = "id"


class RotateImageView(APIView):
    def post(self, request):
        """
        Accepts an image ID and a rotation angle, rotates the image,
        and returns the rotated image.
        """
        serializer = RotateImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document_id = serializer.validated_data["id"]

        try:
            document = Document.objects.get(id=document_id, media_type="image")
        except Document.DoesNotExist:
            return Response(
                {"error": "Image not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        rotation_angle = serializer.validated_data["rotation_angle"]

        try:
            image = Image.open(document.file)
            rotated_image = image.rotate(rotation_angle, expand=True)
            original_format = image.format

            image_io = BytesIO()
            rotated_image.save(image_io, format=original_format)
            image_io.seek(0)

            rotated_image_name = f"{uuid.uuid4()}.{original_format.lower()}"
            rotated_image_file = ContentFile(image_io.read(), name=rotated_image_name)

            rotated_image = Document.objects.create(
                file=rotated_image_file,
                media_type="image",
            )

            document_serializer = ImageSerializer(rotated_image)
            return Response(document_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"errors": f"An error occurred while rotating the image: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConvertPdfToImageView(APIView):
    def post(self, request):
        """
        Accepts a PDF ID, converts the first page of the PDF to an image, and returns the image.
        """
        serializer = ConvertPdfToImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document_id = serializer.validated_data["id"]
        try:
            document = Document.objects.get(id=document_id, media_type="pdf")
        except Document.DoesNotExist:
            return Response(
                {"error": "PDF not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            images = convert_from_path(document.file.path, fmt="jpeg")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        new_images = []
        for image in images:
            image_io = BytesIO()
            original_format = image.format
            image.save(image_io, format=original_format)
            image_io.seek(0)

            image_file = SimpleUploadedFile(
                name=f"{uuid.uuid4()}.jpg",
                content=image_io.read(),
                content_type="image/jpeg",
            )

            new_document = Document.objects.create(
                file=image_file,
                media_type="image",
            )
            new_images.append(new_document)

        return Response(
            {"images": ImageSerializer(new_images, many=True).data},
            status=status.HTTP_201_CREATED,
        )
