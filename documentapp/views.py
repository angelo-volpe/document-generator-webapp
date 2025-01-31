from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

import json
import base64
import requests
import numpy as np
import cv2
from shapely import Polygon
from itertools import product
import pandas as pd

from .models import *
from .forms import DocumentForm
from .logging_config import logger
from .image_utils import align_images, denormalise_box_coordinates, get_box_coords


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

        registered_image = align_images(uploaded_image, template_image)
        _, buffer = cv2.imencode(".png", registered_image)

        encoded_image = base64.b64encode(buffer).decode("utf8")

        data = {"images": [encoded_image]}
        with requests.Session() as session:
            response = session.post(
                f"http://192.168.1.37:8866/predict/ocr_system_document_{document_id}",
                headers={"Content-type": "application/json"},
                data=json.dumps(data),
            )

        if response.status_code != 200:
            logger.error("model prediction failed")
            return render(request, "documentapp/document_prediction.html", context)

        predictions = response.json()["results"]

        if len(predictions) == 0:
            context["base64_document"] = f"data:image/png;base64,{encoded_image}"
            context["predicted_boxes"] = []
            return render(request, "documentapp/document_prediction.html", context)

        predictions = predictions[0]

        doc_height, doc_width = template_image.shape[:2]
        template_boxes = Box.objects.filter(document=document_id)
        template_boxes = BoxSerializer(template_boxes, many=True).data

        template_boxes = map(
            lambda x: {
                "box_name": x["name"],
                "box_id": x["id"],
                "coords": get_box_coords(
                    *denormalise_box_coordinates(
                        x["start_x_norm"],
                        x["start_y_norm"],
                        x["end_x_norm"],
                        x["end_y_norm"],
                        doc_width,
                        doc_height,
                    )
                ),
            },
            template_boxes,
        )

        colliding_boxes = []
        for prediction, label_box in product(predictions, template_boxes):
            pred_poly = Polygon(prediction["text_region"])
            label_poly = Polygon(label_box["coords"])

            pred_area = pred_poly.area
            label_area = label_poly.area
            intersection_area = pred_poly.intersection(label_poly).area

            if intersection_area > 0:
                colliding_boxes.append(
                    {
                        "box_id": label_box["box_id"],
                        "box_name": label_box["box_name"],
                        "detected_box_text": prediction["text"],
                        "detected_box_text_confidence": prediction["confidence"],
                        "intersection_recall": intersection_area / label_area,
                        "intersection_precision": intersection_area / pred_area,
                    }
                )

        colliding_boxes_df = (
            pd.DataFrame(colliding_boxes)
            .sort_values(
                by=["intersection_precision", "intersection_recall"], ascending=False
            )
            .drop_duplicates(subset="box_id")
        )

        context["base64_document"] = f"data:image/png;base64,{encoded_image}"
        context["predicted_boxes"] = colliding_boxes_df.to_dict(orient="records")

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
