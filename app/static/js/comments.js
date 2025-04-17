/**
 * Comments and replies handling for prompts
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get project and prompt IDs from the page
    const projectId = window.location.pathname.split('/')[2];
    const promptId = window.location.pathname.split('/')[4];
    
    // Handle reply button clicks
    document.querySelectorAll('.reply-btn').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            // Hide any other open reply forms
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });
            
            // Toggle this reply form
            replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
            
            // Focus the textarea if we're showing the form
            if (replyForm.style.display === 'block') {
                replyForm.querySelector('textarea').focus();
            }
        });
    });
    
    // Handle cancel reply button clicks
    document.querySelectorAll('.cancel-reply-btn').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            replyForm.style.display = 'none';
        });
    });
    
    // Handle edit comment buttons
    document.querySelectorAll('.edit-comment-btn').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const commentCard = document.getElementById(`comment-${commentId}`);
            const contentDiv = commentCard.querySelector('.comment-content');
            const currentContent = contentDiv.textContent.trim();
            
            // Replace the content with an editable form
            const editForm = document.createElement('form');
            editForm.classList.add('edit-comment-form', 'mt-2', 'mb-3');
            editForm.setAttribute('method', 'POST');
            editForm.setAttribute('action', `/projects/${projectId}/prompts/${promptId}/comments/${commentId}/edit`);
            
            editForm.innerHTML = `
                <div class="mb-2">
                    <textarea class="form-control" name="content" rows="3" required>${currentContent}</textarea>
                </div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-sm btn-outline-secondary me-2 cancel-edit-btn">Cancel</button>
                    <button type="submit" class="btn btn-sm btn-primary">Save changes</button>
                </div>
            `;
            
            // Store the original content to restore if canceled
            editForm.dataset.originalContent = currentContent;
            
            // Hide the content and add the form
            contentDiv.style.display = 'none';
            contentDiv.parentNode.insertBefore(editForm, contentDiv.nextSibling);
            
            // Focus the textarea
            editForm.querySelector('textarea').focus();
            
            // Handle cancel edit
            editForm.querySelector('.cancel-edit-btn').addEventListener('click', function() {
                contentDiv.style.display = 'block';
                editForm.remove();
            });
        });
    });
    
    // Handle edit reply buttons (similar to edit comment)
    document.querySelectorAll('.edit-reply-btn').forEach(button => {
        button.addEventListener('click', function() {
            const replyId = this.getAttribute('data-reply-id');
            const replyDiv = document.getElementById(`reply-${replyId}`);
            const contentDiv = replyDiv.querySelector('.reply-content');
            const currentContent = contentDiv.textContent.trim();
            
            // Create edit form (similar to comment edit form)
            const editForm = document.createElement('form');
            editForm.classList.add('edit-reply-form', 'mt-2');
            editForm.setAttribute('method', 'POST');
            editForm.setAttribute('action', `/projects/${projectId}/prompts/${promptId}/replies/${replyId}/edit`);
            
            editForm.innerHTML = `
                <div class="mb-2">
                    <textarea class="form-control form-control-sm" name="content" rows="2" required>${currentContent}</textarea>
                </div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-sm btn-outline-secondary me-2 cancel-edit-btn">Cancel</button>
                    <button type="submit" class="btn btn-sm btn-primary">Save changes</button>
                </div>
            `;
            
            // Hide content and add form
            contentDiv.style.display = 'none';
            contentDiv.parentNode.insertBefore(editForm, contentDiv.nextSibling);
            editForm.querySelector('textarea').focus();
            
            // Handle cancel
            editForm.querySelector('.cancel-edit-btn').addEventListener('click', function() {
                contentDiv.style.display = 'block';
                editForm.remove();
            });
        });
    });
    
    // Handle delete comment buttons
    document.querySelectorAll('.delete-comment-btn').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this comment? This cannot be undone.')) {
                const commentId = this.getAttribute('data-comment-id');
                
                // Create and submit a form programmatically
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/projects/${projectId}/prompts/${promptId}/comments/${commentId}/delete`;
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
    
    // Handle delete reply buttons
    document.querySelectorAll('.delete-reply-btn').forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this reply? This cannot be undone.')) {
                const replyId = this.getAttribute('data-reply-id');
                
                // Create and submit a form programmatically
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/projects/${projectId}/prompts/${promptId}/replies/${replyId}/delete`;
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
}); 