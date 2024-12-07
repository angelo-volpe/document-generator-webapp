from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, mixins

from .models import Document, DocumentSerializer, Box, BoxSerializer
from .forms import DocumentForm


def document_list(request):
    documents = Document.objects.all()  # Fetch all items from the database
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
    return render(request, 'documentapp/confirm_delete.html', {'document_id': document_id})


def get_document_boxes(request, document_id):
    if request.method == 'GET':
        document = get_object_or_404(Document, id=document_id)
        box_list = document.box.all()
        data = BoxSerializer(box_list, many=True).data

        return JsonResponse(data, safe=False)


class BoxViewSet(viewsets.GenericViewSet, 
                 mixins.CreateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin):
    """
    A simple ViewSet for viewing and editing boxes.
    """
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    lookup_field = 'id'


class DocumentViewSet(viewsets.GenericViewSet, 
                      mixins.RetrieveModelMixin):
    """
    A simple ViewSet for viewing and editing boxes.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'
