document.querySelectorAll('.deleteButton').forEach(button => {
    button.addEventListener('click', function() {
        const recordId = this.getAttribute('data-id');

        fetch(`/record/${recordId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Record deleted successfully');
                // Optionally remove the table row
                this.closest('tr').remove();
            } else {
                alert('Failed to delete the record');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the record');
        });
    });
});

document.querySelectorAll('.editButton').forEach(button => {
    button.addEventListener('click', function() {
        const recordId = this.getAttribute('data-id');
        const data = {
            // Example data to be updated
            name: 'Updated Name',
            value: 'Updated Value'
        };

        fetch(`/record/${recordId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                alert('Record updated successfully');
            } else {
                alert('Failed to update the record');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the record');
        });
    });
});