let startX, startY, endX, endY;
const documentContainer = document.getElementById('document-container')
const documentId = documentContainer.dataset.documentId;
const boxList = document.getElementById(`box-list-${documentId}`);


documentContainer.addEventListener('mousedown', (event) => {
    startX = event.offsetX;
    startY = event.offsetY;
    addBoxElement(startX, startY, 0, 0, "new_box");
});


documentContainer.addEventListener('mousemove', (event) => {
    if (event.buttons !== 1) return;  // Only draw when the mouse is pressed
    endX = event.offsetX;
    endY = event.offsetY;

    box = document.getElementById("new_box");
    box.style.width = `${Math.abs(endX - startX)}px`;
    box.style.height = `${Math.abs(endY - startY)}px`;
    box.style.left = `${Math.min(startX, endX)}px`;
    box.style.top = `${Math.min(startY, endY)}px`;
});


documentContainer.addEventListener('mouseup', () => {
    addBoxForm(startX, startY, endX, endY)
});


function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


function addBoxForm(startX, startY, endX, endY) {
    const newBoxForm = document.createElement('form');

    const input_name = document.createElement('input');
    input_name.type = 'text';
    input_name.placeholder = 'Enter Box name';
    input_name.required = true;

    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.textContent = 'Save Box';
    saveButton.onclick = () => saveBox(input_name, startX, startY, endX, endY);

    // Add input and button to the form
    newBoxForm.appendChild(input_name);
    newBoxForm.appendChild(saveButton);

    boxList.appendChild(newBoxForm);
}


function saveBox(input_name, startX, startY, endX, endY) {
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
            document: documentId,
            name: boxName,
            start_x: startX,
            start_y: startY,
            end_x: endX,
            end_y: endY
        })
    })
    .then(response => {
        if (response.ok) {
            box = document.getElementById("new_box");
            box.remove()
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


function addBoxElement(startX, startY, endX, endY, id) {
    const actual_box = document.createElement('div');
    actual_box.id = id;
    actual_box.className = 'bounding-box';
    actual_box.style.width = `${Math.abs(endX - startX)}px`;
    actual_box.style.height = `${Math.abs(endY - startY)}px`;
    actual_box.style.left = `${Math.min(startX, endX)}px`;
    actual_box.style.top = `${Math.min(startY, endY)}px`;
    actual_box.style.display = 'block';
    documentContainer.appendChild(actual_box)
}


function showBox(boxId) {
    fetch(getSingleBoxUrl.replace("1", boxId),
    {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        box_id = `box-${data.id}`
        box = document.getElementById(box_id)
        
        if (!box) {
            addBoxElement(data.start_x, data.start_y, data.end_x, data.end_y, box_id)
        }
        else {
            box.remove()
        }
    })
}


function fetchDataAndUpdateList() {
    fetch(getBoxesUrl.replace("1", documentId))
        .then(response => response.json())
        .then(data => {
            // Clear the existing list
            boxList.innerHTML = '';

            // Loop through the fetched data and create list items
            data.forEach(box => {
                const boxElement = document.createElement('details');
                boxElement.className = 'accordion-item';
                
                // Create name element
                const boxSummary = document.createElement('summary');
                boxSummary.className = 'accordion-trigger'
                boxSummary.textContent = box.name;
                boxElement.appendChild(boxSummary);
                
                // add position description
                const boxDetails = document.createElement('p');
                boxDetails.className = 'accordion-content'
                boxDetails.textContent = `Position: ${box.start_x} ${box.start_y} ${box.end_x} ${box.end_y}`;
                boxElement.appendChild(boxDetails);

                // Create delete button
                const deleteBoxButton = document.createElement('button');
                deleteBoxButton.textContent = 'Delete Box';
                deleteBoxButton.addEventListener('click', () => {
                    deleteBox(box.id, boxElement);
                });
                boxElement.appendChild(deleteBoxButton);

                // Create show button
                const showBoxButton = document.createElement('button');
                showBoxButton.textContent = 'Show Box';
                showBoxButton.addEventListener('click', () => {
                    showBox(box.id);
                });
                boxElement.appendChild(showBoxButton);

                // Create update button
                const updateBoxButton = document.createElement('button');
                updateBoxButton.textContent = 'Update Box';
                updateBoxButton.addEventListener('click', () => {
                    updateBox(box.id);
                });
                boxElement.appendChild(updateBoxButton);

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