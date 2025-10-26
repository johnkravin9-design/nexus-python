# Read the current layout.html
with open('templates/layout.html', 'r') as f:
    content = f.read()

# Add notification JS before the closing body tag
closing_scripts = '''{% block extra_js %}{% endblock %}
    
    <script>
        // Theme toggle
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Initialize theme
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });

        // Real-time notification updates
        function updateUnreadCount(count) {
            const badge = document.getElementById('unread-badge');
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    </script>
</body>'''

new_scripts = '''{% block extra_js %}{% endblock %}
    
    <!-- Notification System -->
    <script src="{{ url_for('static', filename='js/notifications.js') }}"></script>
    
    <script>
        // Theme toggle
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Initialize theme
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });

        // Real-time notification updates
        function updateUnreadCount(count) {
            const badge = document.getElementById('unread-badge');
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    </script>
</body>'''

content = content.replace(closing_scripts, new_scripts)

# Write the updated content back
with open('templates/layout.html', 'w') as f:
    f.write(content)

print("✅ Added notification JavaScript to layout.html")
