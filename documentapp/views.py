from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .models import Document, BoxCoordinate, BoxCoordinateSerializer
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
    boxes = BoxCoordinate.objects.filter(document=document_id)
    return render(request, 'documentapp/document_detail.html', {'document': document, "boxes": boxes})


def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
        return redirect('documentapp:document_list')
    return render(request, 'documentapp/confirm_delete.html', {'document_id': document_id})


def delete_box(request, box_id):
    if request.method == 'DELETE':
        try:
            box = BoxCoordinate.objects.get(id=box_id)
            box.delete()
            return JsonResponse({'status': 'success'})
        except BoxCoordinate.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Box not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def save_box(request):
    if request.method == 'POST':
        # Get data from AJAX request
        document_id = request.POST.get('document_id')
        name = request.POST.get('name')
        x1, y1 = int(request.POST.get('x1')), int(request.POST.get('y1'))
        x2, y2 = int(request.POST.get('x2')), int(request.POST.get('y2'))
        
        # Get the Document and save the BoxCoordinate
        document = Document.objects.get(id=document_id)
        BoxCoordinate.objects.create(document=document, name=name, x1=x1, y1=y1, x2=x2, y2=y2)
        
        return JsonResponse({'status': 'success', 'message': 'Coordinates saved successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def get_boxes(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    box_list = document.box_coordinates.all()
    data = BoxCoordinateSerializer(box_list, many=True).data

    return JsonResponse(data, safe=False)
