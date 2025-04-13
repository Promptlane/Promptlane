// Initialize Intersection Observer for scroll animations
document.addEventListener('DOMContentLoaded', function() {
  // Make dashboard sections visible with a simple fade-in
  document.querySelectorAll('.dashboard-section').forEach(section => {
    setTimeout(() => {
      section.classList.add('visible');
    }, 100);
  });
  
  // Make stat cards clickable
  setupStatCardLinks();
  
  // Fetch data for dashboard sections
  fetchProjects();
  fetchPrompts();
  fetchTeams();
});

// Make stat cards clickable
function setupStatCardLinks() {
  const statCards = document.querySelectorAll('.stat-card');
  
  statCards.forEach((card, index) => {
    let url = '';
    
    // Determine URL based on card index
    switch(index) {
      case 0: url = '/projects'; break;
      case 1: url = '/prompts'; break;
      case 2: url = '/prompts'; break;
      case 3: url = '/teams'; break;
    }
    
    // Add click event
    card.addEventListener('click', () => window.location.href = url);
  });
}

// Format dates using Moment.js
function formatDate(dateString) {
  return moment(dateString).format('MMM D, YYYY');
}

// Format relative time
function formatRelativeTime(dateString) {
  return moment(dateString).fromNow();
}

// Display error message
function showError(containerId, message) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="empty-state">
      <p><i class="bi bi-exclamation-triangle text-warning me-2"></i>${message}</p>
      <button class="btn btn-primary" onclick="location.reload()">Refresh</button>
    </div>
  `;
}

// Show empty state
function showEmptyState(containerId, itemType, createLink, icon) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div class="empty-state">
      <p><i class="bi ${icon} me-2"></i>You don't have any ${itemType} yet.</p>
      <a href="${createLink}" class="btn btn-primary">Create ${itemType.slice(0, -1)}</a>
    </div>
  `;
}

// Fetch projects data
function fetchProjects() {
  const projectsContainer = document.getElementById('projects-list');
  if (!projectsContainer) return;

  // Show loading spinner
  projectsContainer.innerHTML = `
    <div class="loading-spinner">
      <div class="spinner-border" role="status"></div>
    </div>
  `;

  // Fetch projects from API
  fetch('/api/projects')
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Check if there are any projects
      if (data.length === 0) {
        showEmptyState('projects-list', 'projects', '/projects/new', 'bi-folder-plus');
        return;
      }

      // Create HTML for projects
      let projectsHTML = '';

      // Get only the first 3 projects
      const recentProjects = data.slice(0, 3);

      // Generate project items
      recentProjects.forEach(project => {
        projectsHTML += `
          <div class="item-card" onclick="window.location.href='/projects/${project.id}'">
            <h3 class="item-title">${project.name}</h3>
            <div class="item-meta">
              <span><i class="bi bi-calendar3"></i> ${formatDate(project.created_at)}</span>
              <span><i class="bi bi-clock"></i> ${formatRelativeTime(project.updated_at)}</span>
              <span><i class="bi bi-${project.is_public ? 'unlock' : 'lock'}-fill"></i> ${project.is_public ? 'Public' : 'Private'}</span>
            </div>
            <p class="item-description">${project.description || 'No description provided'}</p>
          </div>
        `;
      });

      projectsContainer.innerHTML = projectsHTML;
    })
    .catch(error => {
      console.error('Error fetching projects:', error);
      showError('projects-list', error.message);
    });
}

// Fetch prompts data
function fetchPrompts() {
  const promptsContainer = document.getElementById('prompts-list');
  if (!promptsContainer) return;

  // Show loading spinner
  promptsContainer.innerHTML = `
    <div class="loading-spinner">
      <div class="spinner-border" role="status"></div>
    </div>
  `;

  // Check if the endpoint exists
  fetch('/api/prompts/recent')
    .then(response => {
      if (response.ok) {
        // Endpoint exists, continue
        return response.json();
      } else {
        console.warn('Recent prompts endpoint not available. Using fallback.');
        // Endpoint doesn't exist, use a fallback to fetch all prompts
        return fetchPromptsFallback();
      }
    })
    .then(data => {
      // Check if there are any prompts
      if (!data || data.length === 0) {
        showEmptyState('prompts-list', 'prompts', '/prompts/new', 'bi-file-earmark-plus');
        return;
      }

      // Create HTML for prompts
      let promptsHTML = '';

      // Get only the first 6 prompts
      const recentPrompts = data.slice(0, 6);

      // Generate prompt items
      recentPrompts.forEach(prompt => {
        promptsHTML += `
          <div class="item-card" onclick="window.location.href='/projects/${prompt.project_id}/prompts/${prompt.id}'">
            <h3 class="item-title">${prompt.name}</h3>
            <div class="item-meta">
              <span><i class="bi bi-folder"></i> ${prompt.project_name || 'Unknown Project'}</span>
              <span><i class="bi bi-tag"></i> ${prompt.version || '1'}</span>
              <span><i class="bi bi-clock"></i> ${prompt.last_used ? formatRelativeTime(prompt.last_used) : 'Never used'}</span>
            </div>
            <p class="item-description">${prompt.description || 'No description provided'}</p>
          </div>
        `;
      });

      promptsContainer.innerHTML = promptsHTML;
    })
    .catch(error => {
      console.error('Error fetching prompts:', error);
      showError('prompts-list', error.message);
    });
}

// Fallback function to get prompts from other endpoints
function fetchPromptsFallback() {
  return new Promise((resolve, reject) => {
    // Try to get all projects first
    fetch('/api/projects')
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
      })
      .then(projects => {
        if (!projects || projects.length === 0) {
          resolve([]);
          return;
        }

        // For simplicity, use the first project to get prompts
        const projectId = projects[0].id;
        
        // Get prompts for this project
        fetch(`/api/projects/${projectId}/prompts`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
          })
          .then(prompts => {
            // Transform the data to match the expected format
            const transformedPrompts = prompts.map(prompt => ({
              id: prompt.id,
              name: prompt.name,
              project_id: projectId,
              project_name: projects[0].name,
              version: prompt.version || '1',
              created_at: prompt.created_at,
              description: prompt.description
            }));
            
            // Sort by creation date (most recent first)
            transformedPrompts.sort((a, b) => 
              new Date(b.created_at) - new Date(a.created_at)
            );
            
            resolve(transformedPrompts);
          })
          .catch(error => {
            console.error('Error in fallback fetching prompts:', error);
            resolve([]); // Return empty array instead of rejecting
          });
      })
      .catch(error => {
        console.error('Error in fallback fetching projects:', error);
        resolve([]); // Return empty array instead of rejecting
      });
  });
}

// Fetch teams data
function fetchTeams() {
  const teamsContainer = document.getElementById('teams-list');
  if (!teamsContainer) return;

  // Show loading spinner
  teamsContainer.innerHTML = `
    <div class="loading-spinner">
      <div class="spinner-border" role="status"></div>
    </div>
  `;

  // Check if the endpoint exists
  fetch('/api/teams')
    .then(response => {
      if (response.ok) {
        // Endpoint exists, continue
        return response.json();
      } else {
        console.warn('Teams endpoint not available. Using fallback.');
        // Endpoint doesn't exist, use a fallback
        return fetchTeamsFallback();
      }
    })
    .then(data => {
      // Check if there are any teams
      if (!data || data.length === 0) {
        showEmptyState('teams-list', 'teams', '/teams/new', 'bi-people-fill');
        return;
      }

      // Create HTML for teams
      let teamsHTML = '';

      // Get only the first 6 teams
      const recentTeams = data.slice(0, 6);

      // Generate team items
      recentTeams.forEach(team => {
        const roleIcon = team.role === 'Owner' ? 'bi-person-fill-gear' : 
                         team.role === 'Admin' ? 'bi-person-fill-lock' : 'bi-person';

        teamsHTML += `
          <div class="item-card" onclick="window.location.href='/teams/id/${team.id}'">
            <h3 class="item-title">${team.name}</h3>
            <div class="item-meta">
              <span><i class="bi ${roleIcon}"></i> ${team.role || 'Member'}</span>
              <span><i class="bi bi-people"></i> ${team.member_count || '1'} members</span>
              <span><i class="bi bi-calendar3"></i> Created ${team.created_at ? formatRelativeTime(team.created_at) : 'recently'}</span>
            </div>
            <p class="item-description">${team.description || 'No description provided'}</p>
          </div>
        `;
      });

      teamsContainer.innerHTML = teamsHTML;
    })
    .catch(error => {
      console.error('Error fetching teams:', error);
      showError('teams-list', error.message);
    });
}

// Fallback function for teams
function fetchTeamsFallback() {
  return new Promise((resolve) => {
    // Try the my-teams endpoint
    fetch('/api/teams?my_teams_only=true')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          // If that fails, try teams UI endpoint
          return fetch('/teams/my')
            .then(response => {
              if (response.ok) {
                // This is an HTML response, so we need to create mock data
                // In a real app, you would extract team data from the HTML
                return [{
                  id: 'default',
                  name: 'Your Team',
                  description: 'Your default team',
                  role: 'Member',
                  member_count: 1,
                  created_at: new Date().toISOString()
                }];
              } else {
                return [];
              }
            })
            .catch(() => []);
        }
      })
      .then(teams => {
        resolve(teams);
      })
      .catch(error => {
        console.error('Error in teams fallback:', error);
        resolve([]);
      });
  });
} 