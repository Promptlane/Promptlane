/**
 * PromptLane Admin Dashboard JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize sidebar toggle functionality
  initSidebar();
  
  // Initialize charts
  initCharts();
  
  // Initialize dashboard interactions
  initDashboardInteractions();
});

/**
 * Initialize sidebar toggle functionality
 */
function initSidebar() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const adminContainer = document.querySelector('.admin-container');
  
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      adminContainer.classList.toggle('sidebar-open');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
      const sidebar = document.querySelector('.admin-sidebar');
      const isSidebarOpen = adminContainer.classList.contains('sidebar-open');
      
      // Check if sidebar is open and click is outside sidebar and toggle button
      if (
        isSidebarOpen && 
        !sidebar.contains(event.target) && 
        !sidebarToggle.contains(event.target) &&
        window.innerWidth < 992
      ) {
        adminContainer.classList.remove('sidebar-open');
      }
    });
  }
  
  // Handle responsive behavior
  window.addEventListener('resize', function() {
    if (window.innerWidth >= 992) {
      adminContainer.classList.remove('sidebar-open');
    }
  });
}

/**
 * Initialize dashboard charts
 */
function initCharts() {
  // User activity chart
  initUserActivityChart();
  
  // Content distribution chart
  initContentDistributionChart();
  
  // System performance chart
  initSystemPerformanceChart();
}

/**
 * Initialize user activity chart
 */
function initUserActivityChart() {
  const ctx = document.getElementById('userActivityChart');
  
  if (!ctx) return;
  
  // Sample data - would be replaced with actual API data
  const labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const loginData = [65, 59, 80, 81, 56, 55, 40];
  const projectData = [28, 48, 40, 19, 86, 27, 90];
  const promptData = [12, 19, 3, 5, 2, 3, 20];
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Logins',
          data: loginData,
          borderColor: '#1a3a6e',
          backgroundColor: 'rgba(26, 58, 110, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Projects',
          data: projectData,
          borderColor: '#17a2b8',
          backgroundColor: 'rgba(23, 162, 184, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Prompts',
          data: promptData,
          borderColor: '#28a745',
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            drawBorder: false
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Initialize content distribution chart
 */
function initContentDistributionChart() {
  const ctx = document.getElementById('contentDistributionChart');
  
  if (!ctx) return;
  
  // Sample data - would be replaced with actual API data
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Projects', 'Prompts', 'Teams', 'Users'],
      datasets: [
        {
          data: [25, 45, 15, 15],
          backgroundColor: [
            '#1a3a6e',
            '#17a2b8',
            '#28a745',
            '#fd7e14'
          ],
          borderWidth: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      },
      cutout: '70%'
    }
  });
}

/**
 * Initialize system performance chart
 */
function initSystemPerformanceChart() {
  const ctx = document.getElementById('systemPerformanceChart');
  
  if (!ctx) return;
  
  // Sample data - would be replaced with actual API data
  const labels = ['12am', '4am', '8am', '12pm', '4pm', '8pm'];
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'API Calls',
          data: [1200, 590, 2500, 3800, 2900, 1500],
          backgroundColor: '#1a3a6e'
        },
        {
          label: 'Response Time (ms)',
          data: [150, 90, 220, 380, 250, 150],
          backgroundColor: '#28a745',
          // Use second y-axis
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'API Calls'
          }
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          grid: {
            drawOnChartArea: false
          },
          title: {
            display: true,
            text: 'Response Time (ms)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Initialize dashboard interactions
 */
function initDashboardInteractions() {
  // Refresh button
  const refreshBtn = document.querySelector('.refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      // Show loading indicator
      this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refreshing...';
      this.disabled = true;
      
      // Simulate refresh (would be replaced with actual API call)
      setTimeout(() => {
        // Reset button
        this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
        this.disabled = false;
        
        // Show success notification
        showNotification('Dashboard refreshed successfully!', 'success');
      }, 1500);
    });
  }
  
  // Time range select
  const timeRangeSelect = document.querySelector('.time-range-select');
  if (timeRangeSelect) {
    timeRangeSelect.addEventListener('change', function() {
      // Would trigger API call to update dashboard data based on selected time range
      const selectedRange = this.value;
      console.log(`Time range changed to: ${selectedRange}`);
      
      // Show loading state
      document.querySelectorAll('.card-body').forEach(card => {
        card.classList.add('loading');
      });
      
      // Simulate loading (would be replaced with actual API call)
      setTimeout(() => {
        // Remove loading state
        document.querySelectorAll('.card-body').forEach(card => {
          card.classList.remove('loading');
        });
        
        // Show success notification
        showNotification(`Dashboard updated for ${selectedRange}`, 'info');
      }, 1000);
    });
  }
}

/**
 * Show notification
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
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
  
  // Add to DOM
  document.body.appendChild(notification);
  
  // Show with animation
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Setup auto-dismiss
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 4000);
  
  // Setup manual dismiss
  notification.querySelector('.notification-close').addEventListener('click', () => {
    notification.classList.remove('show');
    setTimeout(() => {
      notification.remove();
    }, 300);
  });
} 