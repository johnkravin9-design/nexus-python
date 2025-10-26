# Read the current layout.html
with open('templates/layout.html', 'r') as f:
    content = f.read()

# Find the messages nav item and add notifications after it
messages_nav = '''<a class="nav-link {% if request.endpoint == 'messages' %}active{% endif %}" href="{{ url_for('messages') }}">
                        <i class="fas fa-comments me-1"></i>Messages
                        <span class="badge bg-danger ms-1" id="unread-badge" style="display: none;">0</span>
                    </a>'''

notifications_nav = '''<a class="nav-link {% if request.endpoint == 'messages' %}active{% endif %}" href="{{ url_for('messages') }}">
                        <i class="fas fa-comments me-1"></i>Messages
                        <span class="badge bg-danger ms-1" id="unread-badge" style="display: none;">0</span>
                    </a>
                    <!-- Notifications Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" id="notificationDropdown">
                            <i class="fas fa-bell me-1"></i>
                            <span class="badge bg-danger" id="notification-badge" style="display: none;">0</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end" style="width: 350px;">
                            <li class="dropdown-header">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span>Notifications</span>
                                    <button class="btn btn-sm btn-outline-secondary" onclick="markAllAsRead()">Mark all read</button>
                                </div>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <div id="notifications-list" style="max-height: 400px; overflow-y: auto;">
                                <div class="text-center p-3">
                                    <i class="fas fa-bell-slash text-muted mb-2"></i>
                                    <p class="text-muted mb-0">No notifications</p>
                                </div>
                            </div>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-center" href="#">View all notifications</a></li>
                        </ul>
                    </li>'''

# Replace the messages nav with messages + notifications
content = content.replace(messages_nav, notifications_nav)

# Write the updated content back
with open('templates/layout.html', 'w') as f:
    f.write(content)

print("✅ Added notifications dropdown to layout.html")
