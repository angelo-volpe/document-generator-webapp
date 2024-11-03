let startX, startY, endX, endY;
const documentContainer = document.getElementById('document-container')
const box = documentContainer.querySelector('.bounding-box');
const documentId = documentContainer.dataset.documentId;
const boxList = document.getElementById(`box-coordinates-${documentId}`);


documentContainer.addEventListener('mousedown', (event) => {
    startX = event.offsetX;
    startY = event.offsetY;
    box.style.left = `${startX}px`;
    box.style.top = `${startY}px`;
    box.style.width = '0px';
    box.style.height = '0px';
    box.style.display = 'block';
});


documentContainer.addEventListener('mousemove', (event) => {
    if (event.buttons !== 1) return;  // Only draw when the mouse is pressed
    endX = event.offsetX;
    endY = event.offsetY;
    box.style.width = `${Math.abs(endX - startX)}px`;
    box.style.height = `${Math.abs(endY - startY)}px`;
    box.style.left = `${Math.min(startX, endX)}px`;
    box.style.top = `${Math.min(startY, endY)}px`;
});


documentContainer.addEventListener('mouseup', () => {
    addBox(startX, startY, endX, endY)
});


function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


function addBox(x1, y1, x2, y2) {
    const newBox = document.createElement('li');
    const form = document.createElement('form');

    const input_name = document.createElement('input');
    input_name.type = 'text';
    input_name.placeholder = 'Enter Box name';
    input_name.required = true;

    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.textContent = 'Save Box';
    saveButton.onclick = () => saveBox(input_name, x1, y1, x2, y2);

    // Add input and button to the form
    form.appendChild(input_name);
    form.appendChild(saveButton);

    // Add form to the list item, and list item to the list
    newBox.appendChild(form);
    boxList.appendChild(newBox);
}


function saveBox(input_name, x1, y1, x2, y2) {
    const boxName = input_name.value

    if (!boxName) {
        alert('Please enter a name for the new Box.');
        return;
    }

    fetch(saveBoxUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': CSRFToken
        },
        body: new URLSearchParams({
            document_id: documentId,
            name: boxName,
            x1: x1,
            y1: y1,
            x2: x2,
            y2: y2
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            fetchDataAndUpdateList();
        } else {
            alert('Error saving coordinates.');
        }
    })
}


function deleteBox(boxId, boxElement) {
    fetch(deleteBoxUrl.replace("1", boxId),
    {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        }
    })
    .then(response => {
        if (response.ok) {
            // Remove the item from the DOM
            boxElement.remove();
        } else {
            console.error('Failed to delete item');
        }
    })
    .catch(error => console.error('Error deleting item:', error));
}


function fetchDataAndUpdateList() {
    fetch(getBoxesUrl.replace("1", documentId))
        .then(response => response.json())
        .then(data => {
            // Clear the existing list
            boxList.innerHTML = '';

            // Loop through the fetched data and create list items
            data.forEach(box => {
                const boxElement = document.createElement('li');
                // TODO add classes
                // newBoxList.className = 'list-item';
                
                // Create name element
                const boxName = document.createElement('span');
                boxName.textContent = `Name: ${box.name}, Position: ${box.x1} ${box.y1} ${box.x2} ${box.y2}`;
                boxElement.appendChild(boxName);

                // Create delete button
                const deleteBoxButton = document.createElement('button');
                deleteBoxButton.textContent = 'Delete Box';
                deleteBoxButton.addEventListener('click', () => {
                    deleteBox(box.id, boxElement);
                });
                boxElement.appendChild(deleteBoxButton);

                // Append the list item to the list
                boxList.appendChild(boxElement);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Fetch and update the list every 5 seconds
// setInterval(fetchDataAndUpdateList, 5000);  // Fetches data every 5 seconds

// Initial load
fetchDataAndUpdateList();