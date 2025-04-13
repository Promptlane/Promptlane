document.addEventListener('DOMContentLoaded', function() {
  // Helper function to handle API errors consistently
  async function handleApiResponse(response) {
    const result = await response.json();
    
    if (response.ok) {
      return result;
    } else {
      // Get the error message from the response with better structure support
      let errorMessage;
      if (result.detail && typeof result.detail === 'object' && result.detail.error_type) {
        // New structured error format
        errorMessage = result.detail.detail || 'An unexpected error occurred';
      } else if (result.detail && typeof result.detail === 'string') {
        // Standard FastAPI error format
        errorMessage = result.detail;
      } else if (typeof result.detail === 'object' && result.error_type) {
        // Top-level structured error
        errorMessage = result.detail || 'An unexpected error occurred';
      } else {
        // Fallback
        errorMessage = 'An unexpected error occurred';
      }
      
      throw new Error(errorMessage);
    }
  }
  
  // Initialize sidebar toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const adminContainer = document.querySelector('.admin-container');
  
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      adminContainer.classList.toggle('sidebar-open');
    });
  }
  
  // Admin toggle handler
  const toggleAdminButtons = document.querySelectorAll('.grant-admin, .remove-admin');
  let selectedUserId = null;
  let isAdmin = false;
  
  toggleAdminButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      selectedUserId = this.getAttribute('data-userid');
      const username = this.getAttribute('data-username');
      isAdmin = this.classList.contains('grant-admin');
      
      // Update confirmation message and title
      document.getElementById('confirmActionTitle').textContent = isAdmin ? 'Grant Admin Privileges' : 'Remove Admin Privileges';
      document.getElementById('confirmAdminMessage').textContent = 
        `Are you sure you want to ${isAdmin ? 'grant' : 'revoke'} admin privileges for ${username}?`;
      
      // Update warning text
      document.getElementById('privilegeWarningText').textContent = isAdmin ? 
        'Admin users have full access to all systems and can modify any settings.' :
        'Removing admin rights will restrict this user from accessing administrative functions.';
      
      // Update button style
      const confirmBtn = document.getElementById('confirmAdminActionBtn');
      confirmBtn.classList.remove('btn-warning', 'btn-danger', 'btn-success');
      confirmBtn.classList.add(isAdmin ? 'btn-success' : 'btn-danger');
      confirmBtn.innerHTML = isAdmin ? 
        '<i class="bi bi-shield-check me-1"></i> Grant Admin Rights' : 
        '<i class="bi bi-shield-x me-1"></i> Revoke Admin Rights';
      
      // Change icon
      const actionIcon = document.querySelector('.action-icon i');
      actionIcon.classList.remove('bi-shield-exclamation', 'bi-shield-check', 'bi-shield-x');
      actionIcon.classList.add(isAdmin ? 'bi-shield-check' : 'bi-shield-x');
      actionIcon.style.color = isAdmin ? 'var(--success-color)' : 'var(--danger-color)';
      
      // Show modal
      const modal = new bootstrap.Modal(document.getElementById('confirmAdminModal'));
      modal.show();
    });
  });
  
  // Send Invitation functionality (replaces old user creation)
  const sendInvitationBtn = document.getElementById('sendInvitationBtn');
  if (sendInvitationBtn) {
    sendInvitationBtn.addEventListener('click', async function() {
      // Get form values
      const username = document.getElementById('newUsername').value.trim();
      const email = document.getElementById('newEmail').value.trim();
      const isAdmin = document.getElementById('isAdmin').checked;
      const expiryHours = parseInt(document.getElementById('invitationExpiry').value);
      const personalMessage = document.getElementById('invitationMessage').value.trim();
      
      // Validate form
      if (!username || !email) {
        showNotification('Please fill in all required fields', 'error');
        return;
      }
      
      if (!validateEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
      }
      
      // Show loading state
      sendInvitationBtn.disabled = true;
      sendInvitationBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Sending...';
      
      try {
        const response = await fetch('/api/admin/users/invite', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            email,
            is_admin: isAdmin,
            expiry_hours: expiryHours,
            personal_message: personalMessage || undefined
          })
        });
        
        // Use the helper function to handle the response
        await handleApiResponse(response);
        
        // Show success notification
        showNotification(`Invitation sent to ${email} successfully`, 'success');
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
        
        // Reload page to show new user
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } catch (error) {
        // Display specific errors for common cases
        let errorMessage = error.message;
        
        if (errorMessage.includes('Username already exists')) {
          errorMessage = `The username "${username}" is already taken. Please choose a different username.`;
          // Highlight the username field
          document.getElementById('newUsername').classList.add('is-invalid');
        } else if (errorMessage.includes('Email already exists')) {
          errorMessage = `The email "${email}" is already registered in the system.`;
          // Highlight the email field
          document.getElementById('newEmail').classList.add('is-invalid');
        }
        
        showNotification(errorMessage, 'error');
      } finally {
        // Reset button state
        sendInvitationBtn.disabled = false;
        sendInvitationBtn.innerHTML = '<i class="bi bi-envelope-paper me-1"></i> Send Invitation';
      }
    });
    
    // Clear validation styling when user changes input
    document.getElementById('newUsername').addEventListener('input', function() {
      this.classList.remove('is-invalid');
    });
    
    document.getElementById('newEmail').addEventListener('input', function() {
      this.classList.remove('is-invalid');
    });
  }

  // Resend invitation handler
  const resendInviteButtons = document.querySelectorAll('.resend-invite');
  let selectedInviteUserId = null;
  let selectedUserEmail = null;
  
  resendInviteButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      selectedInviteUserId = this.getAttribute('data-userid');
      selectedUserEmail = this.getAttribute('data-email');
      
      // Update message
      document.getElementById('resendInviteEmail').textContent = selectedUserEmail;
      
      // Show modal
      const modal = new bootstrap.Modal(document.getElementById('resendInvitationModal'));
      modal.show();
    });
  });
  
  // Confirm resend invitation
  const confirmResendInviteBtn = document.getElementById('confirmResendInviteBtn');
  if (confirmResendInviteBtn) {
    confirmResendInviteBtn.addEventListener('click', async function() {
      if (!selectedInviteUserId) return;
      
      const expiryHours = parseInt(document.getElementById('resendInvitationExpiry').value);
      
      // Show loading state
      this.disabled = true;
      this.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Processing...';
      
      try {
        const response = await fetch(`/api/admin/users/${selectedInviteUserId}/resend-invite`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            expiry_hours: expiryHours
          })
        });
        
        // Use the helper function to handle the response
        await handleApiResponse(response);
        
        // Show success notification
        showNotification(`Invitation resent to ${selectedUserEmail} successfully`, 'success');
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('resendInvitationModal')).hide();
        
        // Reload page to reflect changes
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } catch (error) {
        // Display specific errors for common cases
        let errorMessage = error.message;
        
        if (errorMessage.includes('not in \'invited\' status')) {
          errorMessage = `This user cannot be re-invited because they are no longer in the invited state.`;
        } else if (errorMessage.includes('not found')) {
          errorMessage = `The user no longer exists in the system.`;
        }
        
        showNotification(errorMessage, 'error');
      } finally {
        // Reset button state
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-envelope-check me-1"></i> Resend Invitation';
      }
    });
  }
  
  // Handle confirm admin action
  document.getElementById('confirmAdminActionBtn').addEventListener('click', async function() {
    if (!selectedUserId) return;
    
    // Show loading state
    this.disabled = true;
    this.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Processing...';
    
    try {
      const response = await fetch(`/api/admin/users/${selectedUserId}/admin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_admin_status: isAdmin
        })
      });
      
      // Use the helper function to handle the response
      await handleApiResponse(response);
      
      // Show success notification
      showNotification(`Admin privileges ${isAdmin ? 'granted' : 'revoked'} successfully`, 'success');
      
      // Close modal
      bootstrap.Modal.getInstance(document.getElementById('confirmAdminModal')).hide();
      
      // Reload page to reflect changes
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      // Display specific errors for common cases
      let errorMessage = error.message;
      
      if (errorMessage.includes('not found')) {
        errorMessage = `The user no longer exists in the system.`;
      } else if (errorMessage.includes('permission') || errorMessage.includes('authorized')) {
        errorMessage = `You don't have permission to change admin privileges.`;
      }
      
      showNotification(errorMessage, 'error');
      
      // Reset button state
      this.disabled = false;
      this.innerHTML = isAdmin ? 
        '<i class="bi bi-shield-check me-1"></i> Grant Admin Rights' : 
        '<i class="bi bi-shield-x me-1"></i> Revoke Admin Rights';
    }
  });
  
  // User search functionality
  const userSearch = document.getElementById('userSearch');
  if (userSearch) {
    userSearch.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      const userRows = document.querySelectorAll('.user-row');
      let visibleCount = 0;
      
      userRows.forEach(row => {
        const userInfo = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        
        if (userInfo.includes(searchTerm)) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });
      
      // Update visible count
      document.querySelector('.page-info').textContent = `Showing ${visibleCount} of ${userRows.length} users`;
    });
  }
  
  // User status filter functionality
  const userStatusFilter = document.getElementById('userStatusFilter');
  if (userStatusFilter) {
    userStatusFilter.addEventListener('change', function() {
      const filterValue = this.value;
      const userRows = document.querySelectorAll('.user-row');
      let visibleCount = 0;
      
      userRows.forEach(row => {
        const isAdminUser = row.getAttribute('data-isadmin') === 'true';
        const userStatus = row.getAttribute('data-status');
        
        let shouldShow = false;
        
        switch(filterValue) {
          case 'all':
            shouldShow = true;
            break;
          case 'admin':
            shouldShow = isAdminUser;
            break;
          case 'regular':
            shouldShow = !isAdminUser && userStatus !== 'invited';
            break;
          case 'invited':
            shouldShow = userStatus === 'invited';
            break;
        }
        
        if (shouldShow) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });
      
      // Update visible count
      document.querySelector('.page-info').textContent = `Showing ${visibleCount} of ${userRows.length} users`;
    });
  }
  
  // Sort options functionality
  const sortOptions = document.getElementById('sortOptions');
  if (sortOptions) {
    sortOptions.addEventListener('change', function() {
      const sortValue = this.value;
      const userRows = Array.from(document.querySelectorAll('.user-row'));
      const tbody = userRows[0].parentNode;
      
      // Sort the rows based on selected option
      userRows.sort((a, b) => {
        const aUsername = a.querySelector('td:nth-child(2) .fw-semibold').textContent;
        const bUsername = b.querySelector('td:nth-child(2) .fw-semibold').textContent;
        const aDate = new Date(a.querySelector('td:nth-child(4) div:first-child').textContent);
        const bDate = new Date(b.querySelector('td:nth-child(4) div:first-child').textContent);
        
        switch (sortValue) {
          case 'newest':
            return bDate - aDate;
          case 'oldest':
            return aDate - bDate;
          case 'a-z':
            return aUsername.localeCompare(bUsername);
          case 'z-a':
            return bUsername.localeCompare(aUsername);
          default:
            return 0;
        }
      });
      
      // Remove existing rows
      userRows.forEach(row => row.remove());
      
      // Append sorted rows
      userRows.forEach(row => {
        tbody.appendChild(row);
      });
    });
  }
  
  // View user details
  const viewUserButtons = document.querySelectorAll('.view-user');
  viewUserButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const userId = this.getAttribute('data-userid');
      const row = document.querySelector(`.user-row[data-userid="${userId}"]`);
      
      if (row) {
        console.log('Displaying user row:', row);
        console.log('User status data:', {
          isAdmin: row.getAttribute('data-isadmin'),
          status: row.getAttribute('data-status')
        });
        
        // Get user data from the row
        const username = row.querySelector('td:nth-child(2) .fw-semibold').textContent;
        const email = row.querySelector('td:nth-child(2) .small.text-muted').textContent;
        const isAdmin = row.getAttribute('data-isadmin') === 'true';
        const userStatus = row.getAttribute('data-status') || 'active';
        const created = row.querySelector('td:nth-child(4) div:first-child').textContent;
        const createdTime = row.querySelector('td:nth-child(4) .small.text-muted').textContent;
        
        // Set values in the modal
        document.getElementById('userDetailName').textContent = username;
        document.getElementById('userDetailEmail').textContent = email;
        document.getElementById('userDetailId').textContent = userId;
        document.getElementById('userDetailCreated').innerHTML = `<i class="bi bi-calendar3 me-1"></i> ${created}`;
        document.getElementById('userInitials').textContent = username.substring(0, 2).toUpperCase();
        
        // Set badges
        const badgesContainer = document.getElementById('userDetailBadges');
        badgesContainer.innerHTML = '';
        
        // Add the appropriate status based on admin status
        if (isAdmin) {
          badgesContainer.innerHTML += `<div style="color:#0d6efd; font-weight:500;"><i class="bi bi-shield-check"></i> Admin</div>`;
        } else {
          badgesContainer.innerHTML += `<div style="color:#6c757d; font-weight:500;"><i class="bi bi-person"></i> Regular User</div>`;
        }
        
        // Add invited badge if applicable
        if (userStatus === 'invited') {
          badgesContainer.innerHTML += `<div style="color:#0dcaf0; font-weight:500; margin-top:5px;"><i class="bi bi-envelope"></i> Invited</div>`;
        }
        
        // Set status text
        if (userStatus === 'invited') {
          document.getElementById('userDetailStatus').innerHTML = `<div style="color:#0dcaf0; font-weight:500;"><i class="bi bi-envelope me-1"></i> Invitation Sent</div>`;
        } else {
          document.getElementById('userDetailStatus').innerHTML = `<div style="color:#198754; font-weight:500;"><i class="bi bi-person-check me-1"></i> Active</div>`;
        }
        
        // Set mock stats for demo purposes
        document.getElementById('userStatsProjects').textContent = Math.floor(Math.random() * 10);
        document.getElementById('userStatsPrompts').textContent = Math.floor(Math.random() * 25);
        document.getElementById('userStatsTeams').textContent = Math.floor(Math.random() * 5);
        document.getElementById('userStatsLogins').textContent = Math.floor(Math.random() * 50) + 1;
        
        // Set last login placeholder
        document.getElementById('userDetailLastLogin').innerHTML = '<i class="bi bi-clock-history me-1"></i> Unknown'; // Would be fetched from API
        
        // Display the modal
        const modal = new bootstrap.Modal(document.getElementById('userDetailModal'));
        modal.show();
      }
    });
  });
  
  // Refresh button animation
  const refreshBtn = document.getElementById('refreshUsers');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      this.disabled = true;
      const icon = this.querySelector('i');
      icon.classList.add('spin-animation');
      
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    });
  }
  
  // Function to show notifications
  function showNotification(message, type = 'info') {
    // Get or create container
    const container = document.getElementById('notificationContainer');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    
    notification.innerHTML = `
      <div class="notification-icon">
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      </div>
      <div class="notification-content">
        ${message}
      </div>
      <button class="notification-close">
        <i class="bi bi-x"></i>
      </button>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Show with animation (small delay to allow DOM to update)
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    // Setup auto-dismiss
    const timeout = setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300); // Remove after animation completes
    }, 5000);
    
    // Setup manual dismiss
    notification.querySelector('.notification-close').addEventListener('click', () => {
      clearTimeout(timeout);
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
  }
  
  // Helper function to validate email
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
}); 