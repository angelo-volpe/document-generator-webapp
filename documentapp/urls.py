from django.urls import path
from . import views

app_name = "documentapp"
urlpatterns = [
    path("", views.document_list, name='document_list'),
    path("<int:document_id>/", views.document_detail, name='document_detail'),
    path("new/", views.add_document, name='add_document'),
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('delete/box/<int:box_id>/', views.delete_box, name='delete_box'),
    path('save_box/', views.save_box, name='save_box'),
    path('box/<int:document_id>', views.get_boxes, name="get_boxes"),
]
