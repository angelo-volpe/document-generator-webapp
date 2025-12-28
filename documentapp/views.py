from typing import Any

import cv2
import numpy as np
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .config import get_ocr_predictor
from .document_processor import DocumentProcessor
from .forms import DocumentForm
from .logging_config import logger
from .models import Box, Document, SampleDocument


def document_list(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("documentapp:document_list")
    else:
        form = DocumentForm()

    documents = Document.objects.all()
    return render(
        request,
        "documentapp/document_list.html",
        {"documents": documents, "form": form},
    )


def document_detail(request: HttpRequest, document_id: int) -> HttpResponse:
    document = get_object_or_404(Document, pk=document_id)
    boxes = Box.objects.filter(document=document_id)
    return render(
        request,
        "documentapp/document_detail.html",
        {"document": document, "boxes": boxes},
    )


def document_prediction(request: HttpRequest, document_id: int) -> HttpResponse:
    context: dict[str, Any] = {"document_id": document_id}

    if request.method == "POST" and request.FILES["image"]:
        image = request.FILES["image"]
        image_data = image.read()  # type: ignore[union-attr]

        image_array = np.frombuffer(image_data, np.uint8)
        uploaded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        template_obj = get_object_or_404(Document, id=document_id)
        template_path = template_obj.image.path
        template_image = cv2.imread(template_path, cv2.IMREAD_COLOR)

        template_boxes = Box.objects.filter(document=document_id)

        image_processor = DocumentProcessor(
            template_image,
            uploaded_image,
            template_boxes,
            ocr_predictor=get_ocr_predictor(),
        )

        image_processor.process_document()

        predicted_boxes = image_processor.detected_boxes_df.to_dict(orient="records")
        logger.debug(f"predictions: {predicted_boxes}")

        context["base64_document"] = f"data:image/png;base64,{image_processor.encoded_image}"

        logger.debug(template_boxes)

        context["predicted_boxes"] = predicted_boxes

        context["template_boxes"] = [
            {
                "coords_norm": [
                    [box.start_x_norm, box.start_y_norm],
                    [box.end_x_norm, box.start_y_norm],
                    [box.end_x_norm, box.end_y_norm],
                    [box.start_x_norm, box.end_y_norm],
                ]
            }
            for box in template_boxes
        ]

    return render(request, "documentapp/document_prediction.html", context)


class SampleDocumentListView(ListView):
    model = SampleDocument
    template_name = "documentapp/sample_document_list.html"
    context_object_name = "sample_documents"
    paginate_by = 15

    def get_queryset(self) -> QuerySet[SampleDocument]:
        queryset = super().get_queryset()
        template_document_id = self.request.GET.get("template_document")

        if template_document_id:
            queryset = queryset.filter(template_document__id=template_document_id)

        return queryset
