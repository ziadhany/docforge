import base64
import shutil
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from docengine.models import Document

TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def api_client():
    return APIClient()

# https://github.com/pytest-dev/pytest-django/issues/1126
@pytest.fixture(autouse=True)
# the other fixtures come from pytest-xdist
# if not using that plugin just hash the current test
def media_setup(settings):
    # setup
    settings.MEDIA_ROOT = (
        Path(settings.BASE_DIR) / "test-media"
    )

    # make sure no old/manual stuff added affects tests
    if settings.MEDIA_ROOT.exists():
        shutil.rmtree(settings.MEDIA_ROOT)
    settings.MEDIA_ROOT.mkdir(parents=True)

    yield
    # cleanup the media so it doesn't cause
    # problems elsewhere
    if settings.MEDIA_ROOT.exists():
        shutil.rmtree(settings.MEDIA_ROOT)

@pytest.fixture
def base64_image_png():
    with open(TEST_DATA_DIR / "test_image.png", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


@pytest.fixture
def base64_image_jpg():
    with open(TEST_DATA_DIR / "test_image.jpg", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


@pytest.fixture
def base64_image_gif():
    with open(TEST_DATA_DIR / "test_image.gif", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


@pytest.fixture
def base64_image_webp():
    with open(TEST_DATA_DIR / "test_image.webp", "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


@pytest.fixture
def base64_pdf():
    with open(TEST_DATA_DIR / "test_document.pdf", "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


@pytest.fixture
def image_document():
    test_image_path = Path(TEST_DATA_DIR / "test_image.jpg")
    with open(test_image_path, "rb") as f:
        uploaded_file = SimpleUploadedFile(
            name="test_image.jpg", content=f.read(), content_type="image/jpeg"
        )

    image = Document(media_type="image", file=uploaded_file)
    image.save()
    return image


@pytest.fixture
def pdf_document():
    test_pdf_path = Path(TEST_DATA_DIR / "test_document.pdf")
    with open(test_pdf_path, "rb") as f:
        uploaded_file = SimpleUploadedFile(
            name="test_document.pdf", content=f.read(), content_type="application/pdf"
        )
    pdf = Document(media_type="pdf", file=uploaded_file)
    pdf.save()
    return pdf


@pytest.mark.django_db
def test_upload_image(
    api_client, base64_image_png, base64_image_jpg, base64_image_gif, base64_image_webp
):
    response = api_client.post(
        "/api/upload/",
        [
            {"file": base64_image_png},
            {"file": base64_image_jpg},
            {"file": base64_image_gif},
            {"file": base64_image_webp},
        ],
        format="json",
    )
    assert response.status_code == 201
    assert "documents" in response.data
    assert len(response.data["documents"]) == 4


@pytest.mark.django_db
def test_upload_pdf(api_client, base64_pdf):
    response = api_client.post("/api/upload/", [{"file": base64_pdf}], format="json")
    assert response.status_code == 201
    assert "documents" in response.data


@pytest.mark.django_db
def test_invalid_file_upload(api_client):
    response = api_client.post(
        "/api/upload/", {"file": "invalid_base64"}, format="json"
    )
    assert response.status_code == 400

    response = api_client.post("/api/upload/", {"file": ""}, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_get_all_images(api_client, image_document):
    response = api_client.get("/api/images/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_all_images_empty(api_client):
    response = api_client.get("/api/images/")
    assert response.status_code == 200
    assert len(response.data) == 0

@pytest.mark.django_db
def test_get_all_pdfs(api_client, pdf_document):
    response = api_client.get("/api/pdfs/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_all_pdfs_empty(api_client):
    response = api_client.get("/api/pdfs/")
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_get_image_details(api_client, image_document):
    response = api_client.get(f"/api/images/{image_document.id}/")
    assert response.status_code == 200
    assert "location" in response.data
    assert response.data.get("width") == 800
    assert response.data.get("height") == 400
    assert response.data.get("channels") == 3


@pytest.mark.django_db
def test_get_pdf_details(api_client, pdf_document):
    response = api_client.get(f"/api/pdfs/{pdf_document.id}/")
    assert response.status_code == 200
    assert "location" in response.data
    assert response.data["num_pages"] == 2
    assert response.data["page_dimensions"] == [
        {"height": 842, "width": 596},
        {"height": 842, "width": 596},
    ]


@pytest.mark.django_db
def test_nonexistent_image_details(api_client):
    response = api_client.get("/api/images/999/")  # invalid id
    assert response.status_code == 404


@pytest.mark.django_db
def test_nonexistent_pdf_details(api_client):
    response = api_client.get("/api/pdfs/999/")  # invalid id
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_image(api_client, image_document):
    assert Document.objects.all().count() == 1
    response = api_client.delete(f"/api/images/{image_document.id}/")
    assert response.status_code == 204
    assert Document.objects.all().count() == 0


@pytest.mark.django_db
def test_delete_pdf(api_client, pdf_document):
    assert Document.objects.all().count() == 1
    response = api_client.delete(f"/api/pdfs/{pdf_document.id}/")
    assert response.status_code == 204
    assert Document.objects.all().count() == 0


@pytest.mark.django_db
def test_rotate_image(api_client, image_document):
    response = api_client.post(
        "/api/rotate/", {"id": image_document.id, "rotation_angle": 90}, format="json"
    )
    assert response.status_code == 201
    assert "location" in response.data
    assert response.data.get("width") == 400
    assert response.data.get("height") == 800
    assert response.data.get("channels") == 3


@pytest.mark.django_db
def test_convert_pdf_to_image(api_client, pdf_document):
    response = api_client.post(
        "/api/convert-pdf-to-image/", {"id": pdf_document.id}, format="json"
    )
    assert response.status_code == 201
    assert len(response.data["images"]) == 2  # two pdf pages
