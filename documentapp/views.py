from django.shortcuts import render, redirect, get_object_or_404

from .models import Document
from .forms import DocumentForm

def item_list(request):
    documents = Document.objects.all()  # Fetch all items from the database
    return render(request, 'documentapp/document_list.html', {'documents': documents})


def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('document_list')  # Redirect to the item list page
    else:
        form = DocumentForm()
    return render(request, 'documentapp/add_document.html', {'form': form})


def document_detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, 'documentapp/document_detail.html', {'document': document})
