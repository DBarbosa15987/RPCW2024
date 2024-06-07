document.addEventListener("DOMContentLoaded", function () {
    const sendButton = document.getElementById("send-button");
    const inputText = document.getElementById("input-text");
    const responsesDiv = document.getElementById("responses");
    const messageServerDiv = document.getElementById("messageServer");

    sendButton.addEventListener("click", function () {
        const text = inputText.value;
        fetch('/handle_input', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        }).then(response => {
            return response.json();
        }).then(data => {
            // Clear previous entries
            responsesDiv.innerHTML = "";
            messageServerDiv.textContent = "Based on the data you gave us we found these job offers available:\n";

            // Process results through a for loop
            for (const result of data.results) {
                // Create new entry
                const newEntry = document.createElement("div");
                newEntry.classList.add("jobListing");

                baseSalary = result['salary_min'];
                intervalSalary = result['salary'];
                salaryCurrencyCode = result['salary_currency_code'];
                locations = result['locations'];
                description = result['description'];
                addUrl = result['url'];

                newEntry.textContent = `Job: ${description}\n`;

                responsesDiv.appendChild(newEntry);
            }

            // Clear input text
            inputText.value = "";
        }).catch(error => {
            console.error('Error:', error);
        });
    });
});
