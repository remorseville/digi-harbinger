class NotificationSystem {
    constructor() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);
        
        // Status banner element (initially null)
        this.statusBanner = null;
        
        // Test button event (remove in production)
        document.getElementById('testButton')?.addEventListener('click', () => {
            this.show('This is a test notification!', 'info');
        });
    }
    
    /**
     * Show a notification with optional link
     * @param {string} text - The message text
     * @param {string} type - Notification type (info, success, warning, error)
     * @param {Object} [link] - Optional link configuration
     * @param {string} [link.text] - Link text
     * @param {string} [link.url] - Link URL
     * @param {boolean} [isStatusBanner=false] - If true, creates a persistent banner
     * @param {string} [bannerId='status-banner'] - ID for the status banner
     * @param {number} [duration=5000] - Display duration (ignored for status banner)
     */
    show(text, type = 'info', link = null, isStatusBanner = false, bannerId = 'status-banner', duration = 5000) {
        if (isStatusBanner) {
            this._showStatusBanner(text, type, bannerId);
            return;
        }
    
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
    
        if (link) {
            notification.innerHTML = `${text} <a href="${link.url}" class="notification-link">${link.text}</a>`;
        } else {
            notification.textContent = text;
        }
    
        this.container.appendChild(notification);
    
        // Show animation
        setTimeout(() => notification.classList.add('show'), 10);
    
        // Auto-hide logic (only if duration > 0)
        let hideTimeout;
        const startHideTimer = () => {
            if (duration > 0) {
                hideTimeout = setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }, duration);
            }
        };
    
        // Start the initial timer
        startHideTimer();
    
        // Pause on hover
        notification.addEventListener('mouseenter', () => {
            if (hideTimeout) {
                clearTimeout(hideTimeout); // Pause auto-hide
            }
        });
    
        // Resume when mouse leaves
        notification.addEventListener('mouseleave', () => {
            startHideTimer(); // Restart the timer
        });
    }
    
    /**
     * Internal method to handle status banner
     */
    _showStatusBanner(text, type, bannerId) {
        // Remove existing banner if it exists
        if (this.statusBanner) {
            this.statusBanner.remove();
        }
        
        // Create new banner
        this.statusBanner = document.createElement('div');
        this.statusBanner.className = `notification ${type} status-banner`;
        this.statusBanner.id = bannerId;
        this.statusBanner.textContent = text;
        
        // Add to top of container
        this.container.insertBefore(this.statusBanner, this.container.firstChild);
        
        // Show immediately (no animation delay)
        setTimeout(() => {
            this.statusBanner.classList.add('show');
        }, 10);
    }
    
    /**
     * Hide the status banner
     */
    hideStatusBanner() {
        if (this.statusBanner) {
            this.statusBanner.classList.remove('show');
            
            // Remove after fade out completes
            setTimeout(() => {
                this.statusBanner.remove();
                this.statusBanner = null;
            }, 300);
        }
    }
    
    /**
     * Update status banner text
     */
    updateStatusBanner(text, type = null) {
        if (this.statusBanner) {
            // Just update the existing banner instead of recreating it
            this.statusBanner.textContent = text;
            if (type) {
                // Reset classes - remove all notification type classes first
                this.statusBanner.className = 'notification status-banner';
                // Add the new type class
                this.statusBanner.classList.add(type);
            }
            // Ensure it stays visible
            this.statusBanner.classList.add('show');
        } else {
            // If no banner exists, create one
            this.show(text, type, null, true);
        }
    }
}

// Initialize the notification system
const notifications = new NotificationSystem();

// Optional: Make it available globally
window.notifications = notifications;

notification.addEventListener('mouseleave', () => {
    setTimeout(startHideTimer, 300); // Waits for fade-out to finish
});


// Regular notification (disappears after 5 seconds)
//notifications.show('This is a regular notification', 'info');

// Notification with link
//notifications.show('Click here to', 'success', {
//    text: 'learn more',
//    url: '/more-info'
//});

// Create status banner (persistent until hidden)
//notifications.show('System status: Online', 'success', null, true, 'system-status-banner');

// Update status banner
//notifications.updateStatusBanner('System status: Maintenance in progress', 'warning');

// Hide status banner
//notifications.hideStatusBanner();