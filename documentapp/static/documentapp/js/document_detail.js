let startX, startY, endX, endY;
const documentContainer = document.getElementById('document-container')
const documentId = documentContainer.dataset.documentId;
const boxForms = document.querySelectorAll("#box-form");
const deleteBoxForms = document.querySelectorAll("#delete-box-form");
const newBoxModal = new bootstrap.Modal(document.getElementById('new-box-modal'));
const newBoxForm = document.getElementById('new-box-form');
const generateSampleForm = document.getElementById('generate-sample-form');


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
    newBoxModal.show()
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


async function triggerGenerateSamplingJob(documentId, numSamples) {
    try {
        const response = await fetch(triggerSamplingJobUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRFToken
            },
            body: JSON.stringify({
                job_args: {
                    "document_id": documentId,
                    "num_samples": numSamples
                }
            }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(`DAG triggered successfully! Job ID: ${data.job_id}`);
        } else {
            const error = await response.json();
            alert(`Error: ${error.error || "Failed to trigger Job"}`);
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("Failed to trigger Job due to a network error.");
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


function createBox(boxName, isNumeric, isAlphabetic, meanLength) {
    if (!boxName) {
        alert('Please enter a name for the new Box.');
        return;
    }

    [startXNorm, startYNorm, endXNorm, endYNorm] = normaliseBoxCoordinates(startX, startY, endX, endY);

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
            end_y_norm: endYNorm,
            is_numeric: isNumeric,
            is_alphabetic: isAlphabetic,
            mean_length: meanLength
        })
    })
    .then(response => {
        if (response.ok) {
            new_box = document.getElementById("new_box");
            new_box.remove()
            console.info("New Box created")
            location.reload(true);
        } else {
            alert("Error saving coordinates.");
        }
    })
}


function deleteBox(boxId) {
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
            console.info('Box deleted')
            location.reload(true);
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

boxForms.forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        const boxId = form.dataset.boxId;
        const isNumeric = form.querySelector(`#is-numeric-${boxId}`).checked;
        const isAlphabetic = form.querySelector(`#is-alphabetic-${boxId}`).checked;
        const meanLength = form.querySelector(`#mean-length-${boxId}`).value;

        updateBox(boxId, isNumeric, isAlphabetic, meanLength);
    });
});

deleteBoxForms.forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        const boxId = form.dataset.boxId;

        deleteBox(boxId);
    });
});

newBoxForm.addEventListener("submit", function(event) {
    event.preventDefault();
    const boxName = newBoxForm.querySelector(`#new-box-name`).value
    const isNumeric = newBoxForm.querySelector(`#new-box-is-numeric`).checked;
    const isAlphabetic = newBoxForm.querySelector(`#new-box-is-alphabetic`).checked;
    const meanLength = newBoxForm.querySelector(`#new-box-mean-length`).value;

    createBox(boxName, isNumeric, isAlphabetic, meanLength);
    newBoxModal.hide();
});

generateSampleForm.addEventListener("submit", function(event) {
    event.preventDefault();
    const numSamples = generateSampleForm.querySelector("#num-samples").value;
    console.info(numSamples);
    deleteSamples(documentId)
    triggerGenerateSamplingJob(documentId, numSamples);
});
