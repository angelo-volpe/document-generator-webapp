from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('box', views.BoxViewSet)

app_name = "documentapp"

urlpatterns = [
    path("", views.document_list, name='document_list'),
    path("<int:document_id>/", views.document_detail, name='document_detail'),
    path("new/", views.add_document, name='add_document'),
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('<int:document_id>/boxes', views.get_document_boxes, name="get_boxes"),
    path("", include(router.urls))
]
