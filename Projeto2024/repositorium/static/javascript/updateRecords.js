let author_counter = 1;
let editor_counter = 0;
let advisor_counter = 0;

function applyAutocomplete(elementId, availableTags) {
    $("#" + elementId).autocomplete({
        source: availableTags
    });
}

// Function to add a new author input
document.getElementById('add-author').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    author_counter++;
    
    // Create a new div for the new author input
    let newDiv = document.createElement('div');
    newDiv.className = 'author-container';
    newDiv.id = 'author_div_' + author_counter;

    // Create a new input for author
    let newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.id = 'author_' + author_counter;
    newInput.name = 'author_' + author_counter;
    newInput.placeholder = '{{auth}}';

    // Create a new remove button for author
    let removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'remove-author';
    removeButton.name = 'remove_author_' + author_counter;
    removeButton.textContent = 'Remove';

    // Append the input and remove button to the new div
    newDiv.appendChild(newInput);
    newDiv.appendChild(removeButton);

    // Append the new div to the container
    document.getElementById('author-container').appendChild(newDiv);

    // Apply autocomplete to the new input
    applyAutocomplete(newInput.id, availableTags);
});

// Function to remove the dynamically added author input
$(document).on('click', '.remove-author', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    // Get the parent div of the remove button and remove it
    $(this).parent('.author-container').remove();
});

// Initialize autocomplete for the first author input
var availableTags = [
    {% for value in allData.contributors %} 
    "{{value.id}} - {{value.name}}",
    {% endfor %} 
];
applyAutocomplete('author_1', availableTags);

// Function to add a new editor input
document.getElementById('add-editor').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    editor_counter++;
    
    // Create a new div for the new editor input
    let newDiv = document.createElement('div');
    newDiv.className = 'editor-container';
    newDiv.id = 'editor_div_' + editor_counter;

    // Create a new input for editor
    let newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.id = 'editor_' + editor_counter;
    newInput.name = 'editor_' + editor_counter;
    newInput.placeholder = '{{auth}}';

    // Append the input to the new div
    newDiv.appendChild(newInput);

    // Append the new div to the container
    document.getElementById('editor-container').appendChild(newDiv);

    // Apply autocomplete to the new input
    applyAutocomplete(newInput.id, availableTags);
});

// Function to remove the dynamically added editor input
$(document).on('click', '.remove-editor', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    // Get the parent div of the remove button and remove it
    $(this).parent('.editor-container').remove();
});

// Function to add a new advisor input
document.getElementById('add-advisor').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    advisor_counter++;
    
    // Create a new div for the new advisor input
    let newDiv = document.createElement('div');
    newDiv.className = 'advisor-container';
    newDiv.id = 'advisor_div_' + advisor_counter;

    // Create a new input for advisor
    let newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.id = 'advisor_' + advisor_counter;
    newInput.name = 'advisor_' + advisor_counter;
    newInput.placeholder = '{{auth}}';

    // Append the input to the new div
    newDiv.appendChild(newInput);

    // Append the new div to the container
    document.getElementById('advisor-container').appendChild(newDiv);

    // Apply autocomplete to the new input
    applyAutocomplete(newInput.id, availableTags);
});

// Function to remove the last advisor input
document.getElementById('remove-advisor').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    if (advisor_counter > 0) {
        // Remove the last advisor container
        let lastadvisorDiv = document.getElementById('advisor_div_' + advisor_counter);
        lastadvisorDiv.parentNode.removeChild(lastadvisorDiv);
        
        // Decrement the counter
        advisor_counter--;
    }
});

// Initialize autocomplete for the first advisor input
applyAutocomplete('advisor_1', availableTags);

// Additional autocomplete initializations for other fields (departments, journals, publishers, funding entity)...

$(function () {
    var departmentTags = [
        {% for value in allData.departments %} 
        "{{value.id}} - {{value.name}}",
        {% endfor %} 
    ];
    $("#department").autocomplete({
        source: departmentTags
    }); 
});

$(function () {
    var journalTags = [
        {% for value in allData.journals %} 
        "{{value.id}} - {{value.name}}",
        {% endfor %} 
    ];
    $("#journal").autocomplete({
        source: journalTags
    }); 
});

$(function () {
    var publisherTags = [
        {% for value in allData.publisher %} 
        "{{value.id}} - {{value.name}}",
        {% endfor %} 
    ];
    $("#publisher").autocomplete({
        source: publisherTags
    }); 
});

$(function () {
    var funderTags = [
        {% for value in allData.funders %} 
        "{{value.id}} - {{value.name}}",
        {% endfor %} 
    ];
    $("#fundingEnt").autocomplete({
        source: funderTags
    }); 
});
