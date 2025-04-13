/**
 * Avatar handling utilities for PromptLane Admin
 */
document.addEventListener('DOMContentLoaded', function() {
  /**
   * Get a consistent color index for a username
   * @param {string} username - The username
   * @return {number} - A number between 1-6
   */
  function getConsistentColorIndex(username) {
    // Simple hash function to get consistent colors
    if (!username || typeof username !== 'string') return 1;
    
    // Sum the character codes of the username as a simple hash
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
      hash += username.charCodeAt(i);
    }
    
    // Return a value from 1-6
    return (hash % 6) + 1;
  }
  
  /**
   * Initializes avatar elements with proper styling and colors
   */
  function initializeAvatars() {
    // Process header profile avatar placeholders specially
    const headerAvatar = document.querySelector('.admin-profile .avatar-placeholder');
    if (headerAvatar) {
      const username = headerAvatar.dataset.user;
      if (username) {
        // Set text if not already set
        if (!headerAvatar.textContent.trim()) {
          headerAvatar.textContent = username.slice(0, 2).toUpperCase();
        }
        
        // Apply styling explicitly to ensure visibility
        headerAvatar.style.display = 'flex';
        headerAvatar.style.alignItems = 'center';
        headerAvatar.style.justifyContent = 'center';
        headerAvatar.style.width = '36px';
        headerAvatar.style.height = '36px';
        headerAvatar.style.borderRadius = '50%';
        headerAvatar.style.marginRight = '8px';
        headerAvatar.style.textTransform = 'uppercase';
        headerAvatar.style.fontWeight = '600';
        
        // Apply color class based on username instead of inline styles
        const colorIndex = getConsistentColorIndex(username);
        
        // Remove any existing color classes
        headerAvatar.classList.forEach(cls => {
          if (cls.startsWith('avatar-color-')) {
            headerAvatar.classList.remove(cls);
          }
        });
        
        // Add the appropriate color class
        headerAvatar.classList.add(`avatar-color-${colorIndex}`);
      }
    }
    
    // Make sure profile image has proper styling
    const profileImg = document.querySelector('.admin-profile .profile-btn img');
    if (profileImg) {
      profileImg.style.width = '36px';
      profileImg.style.height = '36px';
      profileImg.style.borderRadius = '50%';
      profileImg.style.marginRight = '8px';
      profileImg.style.objectFit = 'cover';
      profileImg.style.border = '2px solid rgba(255,255,255,0.2)';
      profileImg.classList.add('profile-avatar');
    }
    
    // Make sure the profile button is styled properly
    const profileBtn = document.querySelector('.admin-profile .profile-btn');
    if (profileBtn) {
      profileBtn.style.display = 'flex';
      profileBtn.style.alignItems = 'center';
      profileBtn.style.borderRadius = '30px';
      profileBtn.style.backgroundColor = 'rgba(255,255,255,0.1)';
    }
    
    // Process all avatar placeholders
    document.querySelectorAll('.avatar-placeholder').forEach(avatar => {
      // Skip header avatar since we already handled it
      if (avatar === headerAvatar) return;
      
      // If text content is missing, try to get it from data-user attribute
      if (!avatar.textContent.trim() && avatar.dataset.user) {
        const username = avatar.dataset.user;
        avatar.textContent = username.slice(0, 2).toUpperCase();
      }
      
      // Apply styling to ensure visibility
      avatar.style.display = 'flex';
      avatar.style.alignItems = 'center';
      avatar.style.justifyContent = 'center';
      avatar.style.textTransform = 'uppercase';
      avatar.style.fontWeight = '600';
      
      // If it's in a sized container (avatar-sm, avatar-md, avatar-lg), respect that sizing
      const parentElement = avatar.parentElement;
      if (parentElement) {
        ['avatar-sm', 'avatar-md', 'avatar-lg'].forEach(size => {
          if (parentElement.classList.contains(size) || avatar.classList.contains(size)) {
            // Don't override specific sizes
            return;
          }
        });
      }
      
      // If no color class, assign a color based on the avatar's text content
      const colorClass = Array.from(avatar.classList).find(cls => cls.startsWith('avatar-color-'));
      if (!colorClass) {
        // Find closest parent with a data-username attribute, or use the text content
        const username = avatar.closest('[data-username]')?.dataset.username || avatar.textContent.trim();
        const colorIndex = getConsistentColorIndex(username);
        avatar.classList.add(`avatar-color-${colorIndex}`);
      }
    });
    
    // Process avatar-sm/md/lg elements
    document.querySelectorAll('.avatar-sm, .avatar-md, .avatar-lg').forEach(avatar => {
      // If not already a color variant, assign one
      const hasColorClass = Array.from(avatar.classList).some(cls => cls.startsWith('avatar-color-'));
      if (!hasColorClass) {
        // We'll use the row's data-userid if available, otherwise the text content
        const row = avatar.closest('tr[data-userid]');
        const userId = row ? row.dataset.userid : '';
        const colorIndex = userId ? (parseInt(userId, 10) % 6) + 1 : 1;
        avatar.classList.add(`avatar-color-${colorIndex}`);
      }
    });
  }
  
  /**
   * Updates the user detail modal avatar when viewing a user
   * @param {string} username - The username to display
   * @param {string} userId - The user ID (optional)
   */
  function updateUserDetailAvatar(username, userId) {
    const avatarElement = document.getElementById('userAvatarPlaceholder');
    if (avatarElement) {
      // Set initials from username
      const initials = username.slice(0, 2).toUpperCase();
      avatarElement.textContent = initials;
      
      // Remove any existing color classes
      avatarElement.classList.forEach(cls => {
        if (cls.startsWith('avatar-color-')) {
          avatarElement.classList.remove(cls);
        }
      });
      
      // Add a color class based on user ID if available, otherwise username
      const colorIndex = userId ? (parseInt(userId, 10) % 6) + 1 : getConsistentColorIndex(username);
      avatarElement.classList.add(`avatar-color-${colorIndex}`);
    }
  }
  
  // Initialize avatars on page load
  initializeAvatars();
  
  // Handle user detail view button clicks
  document.querySelectorAll('.view-user').forEach(button => {
    button.addEventListener('click', function() {
      // Get the username and userId from the row
      const row = this.closest('tr');
      const userId = row.getAttribute('data-userid');
      const usernameElement = row.querySelector('.fw-semibold');
      
      if (usernameElement) {
        const username = usernameElement.textContent.trim();
        // Update the avatar in the detail modal
        updateUserDetailAvatar(username, userId);
      }
    });
  });
  
  // Export functions to window for use by other scripts
  window.avatarUtils = {
    initializeAvatars,
    updateUserDetailAvatar,
    getConsistentColorIndex
  };
}); 