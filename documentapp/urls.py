from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('box', views.BoxViewSet)
router.register('api/documents', views.DocumentViewSet)
router.register('api/sample_documents', views.SampleDocumentViewSet, basename="sample-documents")
router.register('api/sample_boxes', views.SampleBoxViewSet, basename="sample-boxes")

app_name = "documentapp"

urlpatterns = [
    path("", views.document_list, name='document_list'),
    path("<int:document_id>/detail", views.document_detail, name='document_detail'),
    path("<int:document_id>/prediction/", views.document_prediction, name='document_prediction'),
    path('<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('<int:document_id>/boxes', views.get_document_boxes, name="get_boxes"),
    path('sample_documents/', views.SampleDocumentListView.as_view(), name='sample_documents_list'),
    path("trigger_sampling_dag/", views.trigger_sampling_dag, name="trigger_sampling_dag"),
    path("", include(router.urls))
]
