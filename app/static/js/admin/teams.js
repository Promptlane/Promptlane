/**
 * Teams Admin - JavaScript functionality
 */

// Show notification message
function showNotification(message, type = 'info') {
  const container = document.getElementById('notificationContainer');
  if (!container) return;

  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-icon">
      <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info-circle'}"></i>
    </div>
    <div class="notification-content">${message}</div>
    <button class="notification-close"><i class="bi bi-x"></i></button>
  `;

  container.appendChild(notification);

  // Automatically remove notification after 5 seconds
  setTimeout(() => {
    notification.classList.add('notification-hiding');
    setTimeout(() => {
      if (notification.parentNode === container) {
        container.removeChild(notification);
      }
    }, 300);
  }, 5000);

  // Add click handler to close button
  const closeButton = notification.querySelector('.notification-close');
  if (closeButton) {
    closeButton.addEventListener('click', () => {
      notification.classList.add('notification-hiding');
      setTimeout(() => {
        if (notification.parentNode === container) {
          container.removeChild(notification);
        }
      }, 300);
    });
  }
}

// Create a new team
async function createTeam(teamData) {
  try {
    // This would be a real API call in production
    // const response = await fetch('/api/admin/teams', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(teamData),
    // });
    
    // if (!response.ok) {
    //   throw new Error('Failed to create team');
    // }
    
    // const data = await response.json();
    
    // Simulate successful response
    return {
      success: true,
      message: `Team ${teamData.name} created successfully`,
      team: {
        id: 'temp-' + Date.now(),
        name: teamData.name,
        description: teamData.description,
        created_at: new Date().toISOString(),
        members: [],
        projects: []
      }
    };
  } catch (error) {
    console.error('Error creating team:', error);
    throw error;
  }
}

// Delete a team
async function deleteTeam(teamId) {
  try {
    // This would be a real API call in production
    // const response = await fetch(`/api/admin/teams/${teamId}`, {
    //   method: 'DELETE',
    // });
    
    // if (!response.ok) {
    //   throw new Error('Failed to delete team');
    // }
    
    // const data = await response.json();
    
    // Simulate successful response
    return {
      success: true,
      message: 'Team deleted successfully'
    };
  } catch (error) {
    console.error('Error deleting team:', error);
    throw error;
  }
}

// Get team details
async function getTeamDetails(teamId) {
  try {
    // This would be a real API call in production
    // const response = await fetch(`/api/admin/teams/${teamId}`);
    
    // if (!response.ok) {
    //   throw new Error('Failed to fetch team details');
    // }
    
    // const data = await response.json();
    
    // Simulate successful response with mock data
    return {
      success: true,
      team: {
        id: teamId,
        name: 'Team ' + teamId.substring(0, 4),
        description: 'This is a sample team description.',
        created_at: '2023-01-15T12:00:00Z',
        members: [
          { id: 'user1', name: 'John Doe', email: 'john@example.com', role: 'admin' },
          { id: 'user2', name: 'Jane Smith', email: 'jane@example.com', role: 'member' },
        ],
        projects: [
          { id: 'proj1', name: 'Project Alpha', description: 'This is the first project' },
          { id: 'proj2', name: 'Project Beta', description: 'This is the second project' }
        ]
      }
    };
  } catch (error) {
    console.error('Error fetching team details:', error);
    throw error;
  }
}

// Render team member list with avatars
function renderTeamMembers(members, container) {
  if (!members || !members.length) {
    container.innerHTML = '<p class="text-muted">No members in this team yet.</p>';
    return;
  }

  const list = document.createElement('div');
  list.className = 'team-member-list';

  members.forEach((member, index) => {
    const item = document.createElement('div');
    item.className = 'team-member-card';
    
    // Generate initials for avatar
    const initials = member.name.split(' ')
      .map(n => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
    
    item.innerHTML = `
      <div class="member-avatar-placeholder avatar-color-${(index % 6) + 1}">${initials}</div>
      <div class="team-member-name">${member.name}</div>
      <span class="team-member-role ${member.role === 'admin' ? 'admin' : ''}">${member.role}</span>
      <button class="btn btn-sm btn-outline-danger remove-member" data-member-id="${member.id}">
        <i class="bi bi-person-dash"></i> Remove
      </button>
    `;
    
    list.appendChild(item);
  });
  
  container.innerHTML = '';
  container.appendChild(list);
}

// Initialize on document load
document.addEventListener('DOMContentLoaded', function() {
  // Global variables
  let selectedTeamId = null;
  
  // Team detail view functionality
  const viewTeamButtons = document.querySelectorAll('.view-team');
  viewTeamButtons.forEach(btn => {
    btn.addEventListener('click', async function() {
      const teamId = this.getAttribute('data-teamid');
      selectedTeamId = teamId;
      
      // Set up the modal for team details
      document.getElementById('teamDetailContent').innerHTML = `
        <div class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
      `;
      
      // Show the modal while we load details
      const modal = new bootstrap.Modal(document.getElementById('teamDetailModal'));
      modal.show();
      
      try {
        // Fetch team details
        const teamDetails = await getTeamDetails(teamId);
        const team = teamDetails.team;
        
        // Populate the modal with team details
        const detailContent = document.getElementById('teamDetailContent');
        
        const teamDetailHTML = `
          <div class="team-detail-header">
            <div class="team-title">
              <h3 class="mb-1">${team.name}</h3>
              <span class="text-muted">Created on ${new Date(team.created_at).toLocaleDateString()}</span>
            </div>
            <div class="team-actions">
              <button class="btn btn-outline-primary btn-sm edit-team-btn">
                <i class="bi bi-pencil me-1"></i> Edit Team
              </button>
            </div>
          </div>
          
          <div class="team-description mt-3 mb-4">
            ${team.description ? `<p>${team.description}</p>` : '<p class="text-muted">No description provided.</p>'}
          </div>
          
          <div class="team-stats mb-4">
            <div class="stat-item">
              <div class="stat-value">${team.members?.length || 0}</div>
              <div class="stat-label">Members</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">${team.projects?.length || 0}</div>
              <div class="stat-label">Projects</div>
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-8 mb-4">
              <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <h5 class="card-title mb-0">Team Members</h5>
                  <button class="btn btn-sm btn-outline-primary add-member-btn">
                    <i class="bi bi-person-plus me-1"></i> Add Member
                  </button>
                </div>
                <div class="card-body" id="teamMembersContainer">
                  <!-- Member list will be rendered here -->
                </div>
              </div>
            </div>
            
            <div class="col-md-4 mb-4">
              <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                  <h5 class="card-title mb-0">Projects</h5>
                  <button class="btn btn-sm btn-outline-primary add-project-btn">
                    <i class="bi bi-plus me-1"></i> Add
                  </button>
                </div>
                <div class="card-body" id="teamProjectsContainer">
                  <!-- Project list will be rendered here -->
                </div>
              </div>
            </div>
          </div>
        `;
        
        detailContent.innerHTML = teamDetailHTML;
        
        // Render team members
        renderTeamMembers(team.members, document.getElementById('teamMembersContainer'));
        
        // Render team projects
        const projectsContainer = document.getElementById('teamProjectsContainer');
        if (!team.projects || !team.projects.length) {
          projectsContainer.innerHTML = '<p class="text-muted">No projects assigned to this team yet.</p>';
        } else {
          const projectsList = document.createElement('ul');
          projectsList.className = 'team-projects-list';
          
          team.projects.forEach(project => {
            const projectItem = document.createElement('li');
            projectItem.className = 'team-project-item';
            projectItem.innerHTML = `
              <div class="team-project-icon">
                <i class="bi bi-kanban"></i>
              </div>
              <div class="team-project-info">
                <p class="team-project-name">${project.name}</p>
                <p class="team-project-description">${project.description || 'No description'}</p>
              </div>
              <div class="team-project-actions">
                <button class="btn btn-sm btn-outline-danger remove-project" data-project-id="${project.id}">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            `;
            
            projectsList.appendChild(projectItem);
          });
          
          projectsContainer.innerHTML = '';
          projectsContainer.appendChild(projectsList);
        }
        
      } catch (error) {
        document.getElementById('teamDetailContent').innerHTML = `
          <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Failed to load team details: ${error.message || 'Unknown error'}
          </div>
        `;
      }
    });
  });
  
  // Create team form handling
  const createTeamForm = document.getElementById('createTeamForm');
  const saveTeamBtn = document.getElementById('saveNewTeam');
  
  if (createTeamForm && saveTeamBtn) {
    saveTeamBtn.addEventListener('click', async function() {
      const teamName = document.getElementById('newTeamName').value.trim();
      const teamDescription = document.getElementById('newTeamDescription').value.trim();
      
      if (!teamName) {
        showNotification('Please enter a team name', 'error');
        return;
      }
      
      // Show loading state
      saveTeamBtn.disabled = true;
      saveTeamBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Creating...';
      
      try {
        // Create the team
        const result = await createTeam({
          name: teamName,
          description: teamDescription
        });
        
        showNotification(result.message, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createTeamModal'));
        modal.hide();
        
        // Reload the page to show the new team
        setTimeout(() => {
          window.location.reload();
        }, 1000);
        
      } catch (error) {
        showNotification(error.message || 'Failed to create team', 'error');
      } finally {
        // Reset button state
        saveTeamBtn.disabled = false;
        saveTeamBtn.innerHTML = 'Create Team';
      }
    });
  }
  
  // Delete team functionality
  const deleteButtons = document.querySelectorAll('.delete-team');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  
  deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
      selectedTeamId = this.getAttribute('data-teamid');
      const teamName = this.getAttribute('data-teamname');
      
      // Update modal message
      document.getElementById('confirmDeleteMessage').innerHTML = `
        Are you sure you want to delete the team <strong>${teamName}</strong>?<br>
        This action cannot be undone and will remove all team associations.
      `;
      
      // Show confirm modal
      const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
      modal.show();
    });
  });
  
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', async function() {
      if (!selectedTeamId) return;
      
      // Show loading state
      confirmDeleteBtn.disabled = true;
      confirmDeleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Deleting...';
      
      try {
        // Delete the team
        const result = await deleteTeam(selectedTeamId);
        
        showNotification(result.message, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        modal.hide();
        
        // Remove the team row from the table
        const teamRow = document.querySelector(`.team-row[data-teamid="${selectedTeamId}"]`);
        if (teamRow) {
          teamRow.style.opacity = '0';
          setTimeout(() => {
            teamRow.remove();
          }, 300);
        }
        
      } catch (error) {
        showNotification(error.message || 'Failed to delete team', 'error');
      } finally {
        // Reset button state
        confirmDeleteBtn.disabled = false;
        confirmDeleteBtn.innerHTML = 'Delete Team';
      }
    });
  }
}); 