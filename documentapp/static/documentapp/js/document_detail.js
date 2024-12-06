let startX, startY, endX, endY;
const documentContainer = document.getElementById('document-container')
const documentId = documentContainer.dataset.documentId;
const boxList = document.getElementById(`box-list-${documentId}`);


documentContainer.addEventListener('mousedown', (event) => {
    startX = event.offsetX;
    startY = event.offsetY;
    drawBox(startX, startY, startX, startY, "new_box");
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
    addBoxNameForm(startX, startY, endX, endY)
});


function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


function addBoxNameForm(startX, startY, endX, endY) {
    const newBoxForm = document.createElement('form');

    const inputName = document.createElement('input');
    inputName.type = 'text';
    inputName.placeholder = 'Enter Box name';
    inputName.required = true;

    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.textContent = 'Save Box';
    saveButton.onclick = () => saveBox(inputName.value, startX, startY, endX, endY);

    // Add input and button to the form
    newBoxForm.appendChild(inputName);
    newBoxForm.appendChild(saveButton);

    boxList.appendChild(newBoxForm);
}


function saveBox(boxName, startX, startY, endX, endY) {
    if (!boxName) {
        alert('Please enter a name for the new Box.');
        return;
    }

    fetch(BoxListUrl, {
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
    fetch(BoxDetailUrl.replace("1", boxId),
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
}

function updateBox(boxId, isNumeric, isAlphabetic, meanLength) {
    fetch(BoxDetailUrl.replace("1", boxId),
    {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRFToken
        },
        body: JSON.stringify({
            is_numeric: isNumeric,
            is_alphabetic: isAlphabetic,
            mean_length: meanLength
        })
    })
    .then(response => {
        if (response.ok) {
            console.info('Box udated')
        } else {
            console.error('Failed to update box');
        }
    })
}


function drawBox(startX, startY, endX, endY, id) {
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
    const box_id = `box-${boxId}`
    const box = document.getElementById(box_id)

    if (box) {
        box.remove()
    }
    else {
        fetch(BoxDetailUrl.replace("1", boxId),
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
            drawBox(data.start_x, data.start_y, data.end_x, data.end_y, box_id)
        })
    }
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
                
                // Create is Numeric form
                const isNumericForm = document.createElement('form');
                const numericLabel = document.createElement('label');
                const numericCheckbox = document.createElement('input');
                numericLabel.textContent = 'is numeric'
                numericCheckbox.type = 'checkbox';
                numericCheckbox.checked = box.is_numeric
                numericLabel.appendChild(numericCheckbox);
                isNumericForm.appendChild(numericLabel)
                boxElement.appendChild(isNumericForm)

                // Create is Alphabetic form
                const isAlphabeticForm = document.createElement('form');
                const alphabeticLabel = document.createElement('label');
                const alphabeticCheckbox = document.createElement('input');
                alphabeticLabel.textContent = 'is alphabetic'
                alphabeticCheckbox.type = 'checkbox';
                alphabeticCheckbox.checked = box.is_alphabetic
                alphabeticLabel.appendChild(alphabeticCheckbox);
                isAlphabeticForm.appendChild(alphabeticLabel)
                boxElement.appendChild(isAlphabeticForm)

                // Create Mean Length form
                const meanLengthForm = document.createElement('form');
                const meanLengthLabel = document.createElement('label');
                const meanLengthInput = document.createElement('input');
                meanLengthLabel.textContent = 'mean length'
                meanLengthInput.type = 'text';
                meanLengthInput.value = box.mean_length
                meanLengthLabel.appendChild(meanLengthInput);
                meanLengthForm.appendChild(meanLengthLabel)
                boxElement.appendChild(meanLengthForm)

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
                    updateBox(box.id, numericCheckbox.checked, alphabeticCheckbox.checked, meanLengthInput.value);
                });
                boxElement.appendChild(updateBoxButton);

                // Append the list item to the list
                boxList.appendChild(boxElement);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Initial load
fetchDataAndUpdateList();