class NotificationSystem {
    constructor() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);
        
        // Test button event (remove in production)
        document.getElementById('testButton')?.addEventListener('click', () => {
            this.show('This is a test notification!', 'info');
        });
    }
    
    /**
     * Show a notification with optional link
     * @param {string} text - The message text
     * @param {string} type - Notification type
     * @param {Object} [link] - Optional link configuration
     * @param {string} [link.text] - Link text
     * @param {string} [link.url] - Link URL
     * @param {number} [duration=5000] - Display duration
     */
    show(text, type = 'info', link = null, duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        if (link) {
            notification.innerHTML = `
                ${text} <a href="${link.url}">${link.text}</a>
            `;
        } else {
            notification.textContent = text;
        }
        
        this.container.appendChild(notification);
        
        // Trigger the animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Hide after duration
        setTimeout(() => {
            notification.classList.remove('show');
            
            // Remove after fade out completes
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }
}

// Initialize the notification system
const notifications = new NotificationSystem();

// Optional: Make it available globally
window.notifications = notifications;

// Example usage:
// notifications.show('Operation successful!', 'success');
// notifications.show('Something went wrong', 'error');
// notifications.show('Warning: This action cannot be undone', 'warning');
// notifications.show('New message received', 'info');