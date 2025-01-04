import base64

import pytest

# import requests


# Helper function to encode files in base64
def encode_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test_upload_image():
    image_base64 = encode_file("path_to_image.jpg")
    response = requests.post(
        "http://localhost:5000/api/upload/",
        json={"file": image_base64, "file_type": "image"},
    )
    assert response.status_code == 200
    assert "image_id" in response.json()


def test_upload_pdf():
    pdf_base64 = encode_file("path_to_pdf.pdf")
    response = requests.post(
        "http://localhost:5000/api/upload/",
        json={"file": pdf_base64, "file_type": "pdf"},
    )
    assert response.status_code == 200
    assert "pdf_id" in response.json()


#  GET /api/images/
def test_get_images():
    response = requests.get("http://localhost:5000/api/images/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# GET /api/pdfs/
def test_get_pdfs():
    response = requests.get("http://localhost:5000/api/pdfs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# GET /api/pdfs/{id}/
def test_get_image_details():
    image_id = "some_image_id"  # Replace with an actual image ID
    response = requests.get(f"http://localhost:5000/api/images/{image_id}/")
    assert response.status_code == 200
    data = response.json()
    assert "location" in data
    assert "width" in data
    assert "height" in data
    assert "channels" in data
