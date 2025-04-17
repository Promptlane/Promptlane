/**
 * Prompt edit form handler
 * Manages the confirmation modal for updating prompts
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded in prompt-edit.js');
    
    // Check if Bootstrap is loaded
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap is not loaded! Modal functionality will not work.');
        return;
    } else {
        console.log('Bootstrap is loaded, version:', bootstrap.Tooltip.VERSION);
    }
    
    // Get references to the form and modal elements
    // Using more specific selector to match the form in the edit tab
    const editForm = document.querySelector('#edit-tab-pane form');
    console.log('Edit form found:', !!editForm);
    
    const updateRadio = document.getElementById('updateExisting');
    const createNewRadio = document.getElementById('createNew');
    console.log('Radio buttons found:', 
        'updateRadio:', !!updateRadio, 'checked:', updateRadio?.checked,
        'createNewRadio:', !!createNewRadio, 'checked:', createNewRadio?.checked
    );
    
    const modalUpdateRadio = document.getElementById('modalUpdateExisting');
    const modalCreateNewRadio = document.getElementById('modalCreateNew');
    const confirmUpdateBtn = document.getElementById('confirmUpdateBtn');
    const updateConfirmModalEl = document.getElementById('updateConfirmModal');
    
    console.log('Form elements found:', 
        'updateRadio:', !!updateRadio, 
        'createNewRadio:', !!createNewRadio,
        'modalUpdateRadio:', !!modalUpdateRadio,
        'modalCreateNewRadio:', !!modalCreateNewRadio,
        'confirmUpdateBtn:', !!confirmUpdateBtn,
        'updateConfirmModal:', !!updateConfirmModalEl
    );
    
    // Debug form contents
    if (editForm) {
        console.log('Form action:', editForm.action);
        console.log('Form method:', editForm.method);
        
        // Log all form fields
        const formData = new FormData(editForm);
        console.log('Form fields:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
    }
    
    // Add change listeners to radio buttons
    if (updateRadio && createNewRadio) {
        updateRadio.addEventListener('change', function() {
            console.log('Update radio changed, checked:', updateRadio.checked);
        });
        
        createNewRadio.addEventListener('change', function() {
            console.log('Create new radio changed, checked:', createNewRadio.checked);
        });
    }
    
    // Initialize the modal if element exists
    let updateConfirmModal;
    if (updateConfirmModalEl) {
        try {
            updateConfirmModal = new bootstrap.Modal(updateConfirmModalEl);
            console.log('Modal initialized successfully');
        } catch (error) {
            console.error('Error initializing modal:', error);
        }
    } else {
        console.warn('Modal element not found');
    }
    
    // Handle form submission
    if (editForm) {
        editForm.addEventListener('submit', function(event) {
            // Check both radio buttons
            console.log('Form submitted, radio status:', 
                'Update:', updateRadio?.checked, 
                'Create new:', createNewRadio?.checked
            );
            
            // Log all form fields before submission
            const formData = new FormData(editForm);
            console.log('Form submission data:');
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }
            
            // If updating existing version, show confirmation modal
            if (updateRadio && updateRadio.checked && updateConfirmModal) {
                event.preventDefault();
                console.log('Showing confirmation modal for update');
                if (modalUpdateRadio) modalUpdateRadio.checked = true;
                if (modalCreateNewRadio) modalCreateNewRadio.checked = false;
                updateConfirmModal.show();
                return false;
            }
            
            // If creating new version, submit normally
            if (createNewRadio && createNewRadio.checked) {
                console.log('Creating new version, submitting form directly');
                // Make sure version_action is set to new_version
                const versionAction = formData.get('version_action');
                console.log('Version action value before submission:', versionAction);
                return true;
            }
            
            // Otherwise, submit the form normally
            console.log('Form submitted normally');
            return true;
        });
        
        // When confirm button is clicked in the modal
        if (confirmUpdateBtn) {
            confirmUpdateBtn.addEventListener('click', function() {
                console.log('Confirm button clicked');
                console.log('Modal radio selection:', 
                    'Update:', modalUpdateRadio?.checked, 
                    'Create new:', modalCreateNewRadio?.checked
                );
                
                // Update the form's version_action based on modal selection
                if (modalCreateNewRadio && modalCreateNewRadio.checked) {
                    if (createNewRadio) {
                        createNewRadio.checked = true;
                        console.log('Setting createNewRadio to checked');
                    }
                    console.log('Creating new version');
                } else {
                    if (updateRadio) {
                        updateRadio.checked = true;
                        console.log('Setting updateRadio to checked');
                    }
                    console.log('Updating existing version');
                }
                
                // Log form data before submission from modal
                const formData = new FormData(editForm);
                console.log('Form submission data after modal:');
                for (let [key, value] of formData.entries()) {
                    console.log(`${key}: ${value}`);
                }
                
                // Hide the modal and submit the form
                if (updateConfirmModal) updateConfirmModal.hide();
                console.log('Submitting form from modal confirmation');
                editForm.submit();
            });
        }
    }
}); 