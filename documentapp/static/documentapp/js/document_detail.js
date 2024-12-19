let startX, startY, endX, endY;
const documentContainer = document.getElementById('document-container')
const documentId = documentContainer.dataset.documentId;
const boxList = document.getElementById(`box-list-${documentId}`);


document.getElementById("generateSampleButton").addEventListener("click", function() {
    const numSamplesValue = document.getElementById("numSamplesInput").value;
    deleteSamples(documentId)
    triggerGenerateSampleDAG(documentId, numSamplesValue);
});


documentContainer.addEventListener('mousedown', (event) => {
    startX = event.offsetX;
    startY = event.offsetY;
    drawBox(startX, startY, startX, startY, 'new_box');
});


documentContainer.addEventListener('mousemove', (event) => {
    if (event.buttons !== 1) return;  // Only draw when the mouse is pressed
    endX = event.offsetX;
    endY = event.offsetY;

    new_box = document.getElementById('new_box');
    new_box.style.width = `${Math.abs(endX - startX)}px`;
    new_box.style.height = `${Math.abs(endY - startY)}px`;
    new_box.style.left = `${Math.min(startX, endX)}px`;
    new_box.style.top = `${Math.min(startY, endY)}px`;
});


documentContainer.addEventListener('mouseup', () => {
    addBoxNameForm(startX, startY, endX, endY)
});


function deleteSamples(documentId) {
    const url = deleteSamplesUrl + `?template_document=${documentId}`

    fetch(url, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRFToken
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error("Failed to delete related documents.");
        }
    })
}


async function triggerGenerateSampleDAG(documentId, numSamples) {
    try {
        const response = await fetch(triggerSamplingDAGUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRFToken
            },
            body: JSON.stringify({
                conf: {
                    "document_id": documentId,
                    "num_samples": numSamples
                }
            }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(`DAG triggered successfully! Run ID: ${data.dag_run_id}`);
        } else {
            const error = await response.json();
            alert(`Error: ${error.error || "Failed to trigger DAG"}`);
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("Failed to trigger DAG due to a network error.");
    }
}


function normaliseBoxCoordinates(startX, startY, endX, endY) {
    docWidth = documentContainer.clientWidth;
    docHeight = documentContainer.clientHeight;

    startXNorm = startX / docWidth;
    endXNorm = endX / docWidth;
    startYNorm = startY / docHeight;
    endYNorm = endY / docHeight;

    return [startXNorm, startYNorm, endXNorm, endYNorm];
}


function denormaliseBoxCoordinates(startXNorm, startYNorm, endXNorm, endYNorm) {
    docWidth = documentContainer.clientWidth;
    docHeight = documentContainer.clientHeight;

    startX = startXNorm * docWidth;
    endX = endXNorm * docWidth;
    startY = startYNorm * docHeight;
    endY = endYNorm * docHeight;

    return [startX, startY, endX, endY];
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

    [startXNorm, startYNorm, endXNorm, endYNorm] = normaliseBoxCoordinates(startX, startY, endX, endY);
    console.info(startX, startY, endX, endY);
    console.info(startXNorm, startYNorm, endXNorm, endYNorm);

    fetch(BoxListUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': CSRFToken
        },
        body: new URLSearchParams({
            document: documentId,
            name: boxName,
            start_x_norm: startXNorm,
            start_y_norm: startYNorm,
            end_x_norm: endXNorm,
            end_y_norm: endYNorm
        })
    })
    .then(response => {
        if (response.ok) {
            new_box = document.getElementById("new_box");
            new_box.remove()
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
    const boxElementId = `box-${boxId}`
    const box = document.getElementById(boxElementId)

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
            [startX, startY, endX, endY] = denormaliseBoxCoordinates(data.start_x_norm, data.start_y_norm, data.end_x_norm, data.end_y_norm)
            drawBox(startX, startY, endX, endY, boxElementId)
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