/**
 * Prompt edit form handler
 * Manages the confirmation modal for updating prompts
 */

document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('#edit-tab-pane form');
    const confirmUpdateBtn = document.getElementById('confirmUpdateBtn');
    const modalRadios = document.getElementsByName('modalVersionAction');
    const formRadios = document.getElementsByName('version_action');
    
    // Handle form submission with confirmation modal
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Show confirmation modal
            const updateModal = new bootstrap.Modal(document.getElementById('updateConfirmModal'));
            updateModal.show();
        });
    }
    
    // When radio buttons in modal change, update the form radios
    for (let radio of modalRadios) {
        radio.addEventListener('change', function() {
            for (let formRadio of formRadios) {
                if (formRadio.value === this.value) {
                    formRadio.checked = true;
                }
            }
        });
    }
    
    // Handle confirm button click
    if (confirmUpdateBtn) {
        confirmUpdateBtn.addEventListener('click', function() {
            // Submit the form
            editForm.submit();
        });
    }
}); 