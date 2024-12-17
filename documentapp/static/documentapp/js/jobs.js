async function triggerGenerateSampleDAG() {
    try {
        const response = await fetch(triggerSamplingDAGUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRFToken
            },
            body: JSON.stringify({
                conf: {}
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