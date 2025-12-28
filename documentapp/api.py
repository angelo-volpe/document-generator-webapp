import json
import traceback
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .config import get_job_executor
from .jobs import JobType
from .logging_config import logger
from .models import (
    Box,
    BoxSerializer,
    Document,
    DocumentSerializer,
    SampleBox,
    SampleBoxSerializer,
    SampleDocument,
    SampleDocumentSerializer,
)

jobs = get_job_executor()


## Jobs API
@require_http_methods(["POST"])
def trigger_sampling_job(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)

        job_id = jobs.run_job(JobType.SAMPLE_GENERATION, data["job_args"])

        return JsonResponse({"job_id": job_id}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def trigger_model_fine_tuning_job(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)

        job_id = jobs.run_job(JobType.MODEL_FINE_TUNING, data["job_args"])

        return JsonResponse({"job_id": job_id}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


### REST API
class BoxViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    lookup_field = "id"


class DocumentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = "id"

    @action(detail=True, methods=["get"])
    def get_samples(self, request: Request, id: int | None = None) -> Response:
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        samples = document.samples.all()
        serializer = SampleDocumentSerializer(samples, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def get_boxes(self, request: Request, id: int | None = None) -> Response:
        try:
            document = self.get_object()
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        boxes = document.box.all()
        serializer = BoxSerializer(boxes, many=True)
        return Response(serializer.data)


class SampleDocumentViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin
):
    queryset = SampleDocument.objects.all()
    serializer_class = SampleDocumentSerializer
    lookup_field = "id"

    @action(detail=False, methods=["delete"])
    def delete_template_samples(self, request: Request) -> Response:
        try:
            template_document = request.query_params.get("template_document")

            related_documents = SampleDocument.objects.filter(template_document=template_document)
            deleted_count = related_documents.delete()

            return Response(
                {"message": f"Deleted {deleted_count[0]} related SampleDocument(s)."},
                status=status.HTTP_200_OK,
            )
        except Document.DoesNotExist:
            return Response(
                {"error": "Template document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"])
    def get_boxes(self, request: Request, id: int | None = None) -> Response:
        try:
            sample_document = self.get_object()
        except SampleDocument.DoesNotExist:
            return Response(
                {"error": "SampleDocument not found."}, status=status.HTTP_404_NOT_FOUND
            )
        sample_boxes = sample_document.sample_box.all()
        serializer = SampleBoxSerializer(sample_boxes, many=True)
        return Response(serializer.data)


class SampleBoxViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = SampleBox.objects.all()
    serializer_class = SampleBoxSerializer
    lookup_field = "id"

    @action(detail=False, methods=["post"])
    def create_sample_boxes(self, request: Request) -> Response:
        try:
            data = request.data
            sample_document_id = data.get("sample_document_id")
            boxes: list[dict[str, Any]] = data.get("boxes", [])

            for box in boxes:
                template_box_id = box.pop("template_box_id")
                SampleBox.objects.create(
                    sample_document_id=sample_document_id,
                    template_box_id=template_box_id,
                    **box,
                )

            return Response(
                {"message": f"Created {len(boxes)} SampleBox(es)."},
                status=status.HTTP_201_CREATED,
            )
        except SampleDocument.DoesNotExist:
            return Response(
                {"error": "SampleDocument not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
