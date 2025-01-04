from io import BytesIO

from django.core.files.base import ContentFile
from pdf2image import convert_from_path
from PIL import Image
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from docengine.serializer import (DocumentSerializer, ImageSerializer,
                                  MultipleDocumentUploadSerializer,
                                  PdfSerializer)

from .models import Document


class DocumentUploadView(APIView):
    """ """

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = MultipleDocumentUploadSerializer(data=data, many=True)
        if serializer.is_valid():
            documents = serializer.save()
            return Response(
                {
                    "message": "Documents uploaded successfully",
                    "documents": [doc.id for doc in documents],
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
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


class ImageDetailView(RetrieveDestroyAPIView):
    """ """

    queryset = Document.objects.filter(media_type="image")
    serializer_class = ImageSerializer
    lookup_field = "id"


class PdfDetailView(RetrieveDestroyAPIView):
    """ """

    queryset = Document.objects.filter(media_type="pdf")
    serializer_class = PdfSerializer
    lookup_field = "id"


class RotateImageView(APIView):
    """
    Accepts an image ID and a rotation angle, rotates the image,
    and returns the rotated image.
    """

    def post(self, request, id):
        # Fetch the document using the provided ID
        try:
            document = Document.objects.get(id=id, media_type="image")
        except Document.DoesNotExist:
            return Response(
                {"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Get the rotation angle from the request data
        rotation_angle = request.data.get("rotation_angle", None)
        if rotation_angle is None:
            return Response(
                {"detail": "Rotation angle is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rotation_angle = float(rotation_angle)
        except ValueError:
            return Response(
                {"detail": "Invalid rotation angle."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = Image.open(document.file)
        rotated_image = image.rotate(rotation_angle, expand=True)
        image_io = BytesIO()
        rotated_image.save(image_io, format="JPEG")
        image_io.seek(0)

        rotated_image_name = f"rotated_{document.id}.jpg"

        rotated_image_file = ContentFile(image_io.read(), name=rotated_image_name)

        rotated_document = Document.objects.create(
            file=rotated_image_file,
            media_type="image",
        )

        serializer = DocumentSerializer(rotated_document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConvertPdfToImageView(APIView):
    """
    Accepts a PDF ID, converts the first page of the PDF to an image, and returns the image.
    """

    def post(self, request):
        pdf_id = request.data.get("pdf_id")

        if not pdf_id:
            return Response(
                {"detail": "PDF ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = Document.objects.get(id=pdf_id, media_type="pdf")
        except Document.DoesNotExist:
            return Response(
                {"detail": "PDF not found."}, status=status.HTTP_404_NOT_FOUND
            )

        pdf_path = document.file.path

        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        image = images[0]
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)

        image_name = f"pdf_page_{document.id}.jpg"
        image_file = ContentFile(image_io.read(), name=image_name)

        new_document = Document.objects.create(
            file=image_file,
            media_type="image",
        )

        return Response(
            {"image_url": new_document.file.url}, status=status.HTTP_201_CREATED
        )
