from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

import numpy as np
import cv2

from .models import *
from .forms import DocumentForm
from .document_processor import DocumentProcessor
from .ocr_predictor import PaddleAPIOCRPredictor
from .logging_config import logger


def document_list(request):
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


def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    boxes = Box.objects.filter(document=document_id)
    return render(
        request,
        "documentapp/document_detail.html",
        {"document": document, "boxes": boxes},
    )


def document_prediction(request, document_id):
    context = {"document_id": document_id}

    if request.method == "POST" and request.FILES["image"]:
        image = request.FILES["image"]
        image_data = image.read()

        image_array = np.frombuffer(image_data, np.uint8)
        uploaded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        template_obj = get_object_or_404(Document, id=document_id)
        template_path = template_obj.image.path
        template_image = cv2.imread(template_path, cv2.IMREAD_COLOR)

        template_boxes = Box.objects.filter(document=document_id)
        template_boxes = BoxSerializer(template_boxes, many=True).data

        image_processor = DocumentProcessor(
            template_image,
            uploaded_image,
            template_boxes,
            PaddleAPIOCRPredictor(document_id=document_id),
        )

        image_processor.process_document()

        predicted_boxes = image_processor.detected_boxes_df.to_dict(orient="records")
        logger.debug(f"predictions: {predicted_boxes}")

        context["base64_document"] = (
            f"data:image/png;base64,{image_processor.encoded_image}"
        )

        logger.debug(template_boxes)

        context["predicted_boxes"] = predicted_boxes
                
        context["template_boxes"] = list(map(lambda x: {"coords_norm": [[x["start_x_norm"], x["start_y_norm"]], 
                                                                        [x["end_x_norm"], x["start_y_norm"]], 
                                                                        [x["end_x_norm"], x["end_y_norm"]], 
                                                                        [x["start_x_norm"], x["end_y_norm"]]]}, 
                                            template_boxes))

    return render(request, "documentapp/document_prediction.html", context)


class SampleDocumentListView(ListView):
    model = SampleDocument
    template_name = "documentapp/sample_document_list.html"
    context_object_name = "sample_documents"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        template_document_id = self.request.GET.get("template_document")

        if template_document_id:
            queryset = queryset.filter(template_document__id=template_document_id)

        return queryset
