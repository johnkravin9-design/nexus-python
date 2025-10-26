// Notification system with push notifications
class NotificationSystem {
    constructor() {
        this.notificationCount = 0;
        this.socket = io();
        this.setupServiceWorker();
        this.setupSocketListeners();
        this.updateNotificationCount();
        this.setupNotificationBell();
    }

    // Setup Service Worker for push notifications
    async setupServiceWorker() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('Service Worker registered');

                // Request notification permission
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    console.log('Push notifications granted');
                    this.subscribeToPush(registration);
                }
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        }
    }

    // Subscribe to push notifications
    async subscribeToPush(registration) {
        try {
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY') // You'll need to generate this
            });
            
            // Send subscription to server
            await fetch('/push/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscription)
            });
        } catch (error) {
            console.log('Push subscription failed:', error);
        }
    }

    // Setup Socket.IO listeners
    setupSocketListeners() {
        this.socket.on('new_notification', (data) => {
            this.showNotification(data);
            this.updateNotificationCount();
        });

        this.socket.on('notification_read', () => {
            this.updateNotificationCount();
        });
    }

    // Show notification (both in-app and push)
    showNotification(data) {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(data.title, {
                body: data.message,
                icon: '/static/icon.png',
                tag: data.type
            });

            notification.onclick = function() {
                window.focus();
                this.close();
                
                // Navigate based on notification type
                switch(data.type) {
                    case 'like':
                        window.location.href = `/post/${data.related_id}`;
                        break;
                    case 'comment':
                        window.location.href = `/post/${data.related_id}`;
                        break;
                    case 'message':
                        window.location.href = '/messages';
                        break;
                    default:
                        window.location.href = '/notifications';
                }
            };
        }

        // In-app notification toast
        this.showToast(data);
    }

    // Show in-app toast notification
    showToast(data) {
        const toast = document.createElement('div');
        toast.className = `notification-toast notification-${data.type}`;
        toast.innerHTML = `
            <div class="toast-header">
                <strong>${data.title}</strong>
                <button class="toast-close">&times;</button>
            </div>
            <div class="toast-body">${data.message}</div>
        `;

        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-left: 4px solid #007bff;
            padding: 1rem;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);

        // Close button
        toast.querySelector('.toast-close').onclick = () => toast.remove();
        
        // Click to navigate
        toast.onclick = () => {
            this.markAsRead(data.id);
            toast.remove();
        };
    }

    // Setup notification bell in navbar
    setupNotificationBell() {
        const bellHTML = `
            <div class="notification-bell">
                <button class="bell-btn" onclick="notificationSystem.toggleDropdown()">
                    🔔
                    <span class="notification-count" id="notificationCount">0</span>
                </button>
                <div class="notification-dropdown" id="notificationDropdown">
                    <div class="dropdown-header">
                        <h4>Notifications</h4>
                        <button onclick="notificationSystem.markAllAsRead()">Mark all read</button>
                    </div>
                    <div class="dropdown-content" id="notificationList">
                        <div class="loading">Loading...</div>
                    </div>
                    <div class="dropdown-footer">
                        <a href="/notifications">View all</a>
                    </div>
                </div>
            </div>
        `;

        // Add to navbar (you'll need to adjust based on your navbar structure)
        const navbar = document.querySelector('.navbar-nav') || document.querySelector('nav');
        if (navbar) {
            const bellContainer = document.createElement('li');
            bellContainer.className = 'nav-item';
            bellContainer.innerHTML = bellHTML;
            navbar.appendChild(bellContainer);
        }

        this.loadRecentNotifications();
    }

    // Toggle notification dropdown
    toggleDropdown() {
        const dropdown = document.getElementById('notificationDropdown');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        if (dropdown.style.display === 'block') {
            this.loadRecentNotifications();
        }
    }

    // Load recent notifications
    async loadRecentNotifications() {
        const response = await fetch('/api/notifications/recent');
        const notifications = await response.json();
        
        const list = document.getElementById('notificationList');
        if (notifications.length === 0) {
            list.innerHTML = '<div class="no-notifications">No new notifications</div>';
            return;
        }

        list.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.is_read ? 'read' : 'unread'}" 
                 onclick="notificationSystem.openNotification(${notif.id}, '${notif.type}')">
                <div class="notification-title">${notif.title}</div>
                <div class="notification-message">${notif.message}</div>
                <div class="notification-time">${notif.time}</div>
            </div>
        `).join('');
    }

    // Update notification count
    async updateNotificationCount() {
        const response = await fetch('/notifications/count');
        const data = await response.json();
        this.notificationCount = data.count;
        
        const countElement = document.getElementById('notificationCount');
        if (countElement) {
            countElement.textContent = this.notificationCount;
            countElement.style.display = this.notificationCount > 0 ? 'block' : 'none';
        }

        // Update browser tab title
        if (this.notificationCount > 0) {
            document.title = `(${this.notificationCount}) Nexus App`;
        } else {
            document.title = 'Nexus App';
        }
    }

    // Mark notification as read
    async markAsRead(notificationId) {
        await fetch(`/notifications/read/${notificationId}`, {
            method: 'POST'
        });
        this.updateNotificationCount();
    }

    // Mark all as read
    async markAllAsRead() {
        await fetch('/notifications/read-all', {
            method: 'POST'
        });
        this.updateNotificationCount();
        this.loadRecentNotifications();
    }

    // Utility function for VAPID key
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

// Initialize notification system
const notificationSystem = new NotificationSystem();

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.notification-bell')) {
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }
});

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .notification-bell {
        position: relative;
    }

    .bell-btn {
        background: none;
        border: none;
        font-size: 1.5rem;
        position: relative;
        cursor: pointer;
    }

    .notification-count {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #ff4757;
        color: white;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
        display: none;
    }

    .notification-dropdown {
        display: none;
        position: absolute;
        top: 100%;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        width: 300px;
        max-height: 400px;
        overflow-y: auto;
        z-index: 1000;
    }

    .notification-item {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
        cursor: pointer;
    }

    .notification-item.unread {
        background: #f8f9fa;
        font-weight: bold;
    }

    .notification-item:hover {
        background: #e9ecef;
    }

    .notification-title {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }

    .notification-message {
        font-size: 0.9rem;
        color: #666;
    }

    .notification-time {
        font-size: 0.8rem;
        color: #999;
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(style);
