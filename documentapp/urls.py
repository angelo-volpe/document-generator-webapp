from django.urls import path, include
from . import views
from . import api

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("api/box", api.BoxViewSet, basename="box")
router.register("api/documents", api.DocumentViewSet, basename="documents")
router.register(
    "api/sample_documents", api.SampleDocumentViewSet, basename="sample-documents"
)
router.register("api/sample_boxes", api.SampleBoxViewSet, basename="sample-boxes")

app_name = "documentapp"

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("<int:document_id>/detail", views.document_detail, name="document_detail"),
    path(
        "<int:document_id>/prediction/",
        views.document_prediction,
        name="document_prediction",
    ),
    path(
        "sample_documents/",
        views.SampleDocumentListView.as_view(),
        name="sample_documents_list",
    ),
    path(
        "trigger_sampling_job/", api.trigger_sampling_job, name="trigger_sampling_job"
    ),
    path(
        "trigger_model_fine_tuning_job/", api.trigger_model_fine_tuning_job, name="trigger_model_fine_tuning_job"
    ),
    path("", include(router.urls)),
]
