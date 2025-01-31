const deleteDocumentForms = document.querySelectorAll("#delete-document-form");


function deleteDocument(documentId) {
    fetch(DocumentDetailUrl.replace("1", documentId),
    {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        }
    })
    .then(response => {
        if (response.ok) {
            console.info('Document deleted')
            location.reload(true);
        } else {
            console.error('Failed to delete document');
        }
    })
}


deleteDocumentForms.forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        const documentId = form.dataset.documentId;

        deleteDocument(documentId);
    });
});
