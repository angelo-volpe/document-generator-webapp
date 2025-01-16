from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from requests.auth import HTTPBasicAuth
import json
import base64
import requests
import numpy as np
import traceback
import cv2

from .models import *
from .forms import DocumentForm
from .logging_config import logger
from .image_utils import align_images


AIRFLOW_API_URL = "http://airflow-webserver:8080/api/v1/dags"
AIRFLOW_USER = "airflow"
AIRFLOW_PASSWORD = "airflow"


def document_list(request):
    documents = Document.objects.all()
    return render(request, 'documentapp/document_list.html', {'documents': documents})


def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('documentapp:document_list')
    else:
        form = DocumentForm()
    return render(request, 'documentapp/add_document.html', {'form': form})


def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    boxes = Box.objects.filter(document=document_id)
    return render(request, 'documentapp/document_detail.html', {'document': document, "boxes": boxes})


def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
    return redirect('documentapp:document_list')


def document_prediction(request, document_id):
    context = {"document_id": document_id}

    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        image_data = image.read()

        image_array = np.frombuffer(image_data, np.uint8)
        uploaded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        template_obj = get_object_or_404(Document, id=document_id)
        template_path = template_obj.image.path
        template_image = cv2.imread(template_path, cv2.IMREAD_COLOR)
        
        registered_image = align_images(uploaded_image, template_image)
        _, buffer = cv2.imencode('.png', registered_image)

        encoded_image = base64.b64encode(buffer).decode("utf8")
        
        data = {"images": [encoded_image]}
        with requests.Session() as session:
            response = session.post(
                f"http://192.168.1.37:8866/predict/ocr_system_document_{document_id}",
                headers={"Content-type": "application/json"},
                data=json.dumps(data)
            )
        
        if response.status_code != 200:
            logger.error("model prediction failed")
            return render(request, 'documentapp/document_prediction.html', context)

        predictions = response.json()["results"][0]
        
        context["base64_document"] = f"data:image/png;base64,{encoded_image}"
        context["predictions"] = predictions
    
    return render(request, 'documentapp/document_prediction.html', context)


def get_document_boxes(request, document_id):
    if request.method == 'GET':
        document = get_object_or_404(Document, id=document_id)
        box_list = document.box.all()
        data = BoxSerializer(box_list, many=True).data

        return JsonResponse(data, safe=False)


class SampleDocumentListView(ListView):
    model = SampleDocument
    template_name = "documentapp/sample_document_list.html"
    context_object_name = "sample_documents"

    def get_queryset(self):
        queryset = super().get_queryset()
        template_document_id = self.request.GET.get('template_document')
        
        if template_document_id:
            queryset = queryset.filter(template_document__id=template_document_id)
        
        return queryset


## Jobs API
def trigger_sampling_dag(request):
    if request.method == "POST":
        try:
            dag_id = "generate_document_samples"
            data = json.loads(request.body)
            conf = data.get("conf", {})
            
            url = f"{AIRFLOW_API_URL}/{dag_id}/dagRuns"

            with requests.Session() as session:
                response = session.post(
                    url,
                    json={"conf": conf},
                    auth=HTTPBasicAuth(AIRFLOW_USER, AIRFLOW_PASSWORD),
                    timeout=10
                )
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


### REST API
class BoxViewSet(viewsets.GenericViewSet, 
                 mixins.CreateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    lookup_field = 'id'


class DocumentViewSet(viewsets.GenericViewSet, 
                      mixins.RetrieveModelMixin):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'

    @action(detail=True, methods=["get"])
    def get_samples(self, request, id=None):
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response({
                "error": "Document not found."
            }, status=status.HTTP_404_NOT_FOUND)
        samples = document.samples.all()
        serializer = SampleDocumentSerializer(samples, many=True)
        return Response(serializer.data)


class SampleDocumentViewSet(viewsets.GenericViewSet, 
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin):
    queryset = SampleDocument.objects.all()
    serializer_class = SampleDocumentSerializer
    lookup_field = 'id'

    @action(detail=False, methods=["delete"])
    def delete_template_samples(self, request):
        try:
            template_document = request.query_params.get("template_document")

            related_documents = SampleDocument.objects.filter(template_document=template_document)
            deleted_count = related_documents.delete()

            return Response({
                "message": f"Deleted {deleted_count[0]} related SampleDocument(s)."
            }, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({
                "error": "Template document not found."
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=["get"])
    def get_boxes(self, request, id=None):
        try:
            sample_document = self.get_object()
        except SampleDocument.DoesNotExist:
            return Response({
                "error": "SampleDocument not found."
            }, status=status.HTTP_404_NOT_FOUND)
        sample_boxes = sample_document.sample_box.all()
        serializer = SampleBoxSerializer(sample_boxes, many=True)
        return Response(serializer.data)


class SampleBoxViewSet(viewsets.GenericViewSet, 
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       ):
    queryset = SampleBox.objects.all()
    serializer_class = SampleBoxSerializer
    lookup_field = 'id'

    @action(detail=False, methods=["post"])
    def create_sample_boxes(self, request):
        try:
            data = request.data
            sample_document_id = data.get("sample_document_id")
            boxes = data.get("boxes", [])

            for box in boxes:
                template_box_id = box.pop("template_box_id")
                SampleBox.objects.create(sample_document_id=sample_document_id, 
                                         template_box_id=template_box_id, 
                                         **box)

            return Response({
                "message": f"Created {len(boxes)} SampleBox(es)."
            }, status=status.HTTP_201_CREATED)
        except SampleDocument.DoesNotExist:
            return Response({
                "error": "SampleDocument not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
