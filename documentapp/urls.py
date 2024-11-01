from django.urls import path
from . import views

app_name = "documentapp"
urlpatterns = [
    path("", views.item_list, name='document_list'),
    path("<int:document_id>", views.document_detail, name='document_detail'),
    path("new/", views.add_document, name='add_document'),
]
