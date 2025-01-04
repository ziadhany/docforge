"""
URL configuration for docforge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from docengine.views import (ConvertPdfToImageView, DocumentUploadView,
                             ImageDetailView, ImageListView, PdfDetailView,
                             PdfListView, RotateImageView)

urlpatterns = [
    path("upload/", DocumentUploadView.as_view(), name="upload"),
    path("images/", ImageListView.as_view(), name="images-list"),
    path("pdfs/", PdfListView.as_view(), name="pdfs-list"),
    path("images/<uuid:id>/", ImageDetailView.as_view(), name="image-details"),
    path("pdfs/<uuid:id>/", PdfDetailView.as_view(), name="pdf-details"),
    path("rotate/", RotateImageView.as_view(), name="image-rotate"),
    path(
        "convert-pdf-to-image/",
        ConvertPdfToImageView.as_view(),
        name="convert-pdf-to-image",
    ),
]
