from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("api/box", views.BoxViewSet, basename="box")
router.register("api/documents", views.DocumentViewSet, basename="documents")
router.register(
    "api/sample_documents", views.SampleDocumentViewSet, basename="sample-documents"
)
router.register("api/sample_boxes", views.SampleBoxViewSet, basename="sample-boxes")

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
        "trigger_sampling_job/", views.trigger_sampling_job, name="trigger_sampling_job"
    ),
    path("", include(router.urls)),
]
