// Fix for likes and comments not updating dynamically

// Like functionality
function likePost(postId) {
    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }
        
        // Update like button and count
        const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
        const likeCount = document.querySelector(`.like-count[data-post-id="${postId}"]`);
        
        if (likeBtn) {
            likeBtn.classList.toggle('active', data.liked);
            likeBtn.innerHTML = data.liked ? '❤️ Liked' : '🤍 Like';
        }
        
        if (likeCount) {
            likeCount.textContent = data.like_count;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Comment functionality
function submitComment(postId) {
    const content = document.querySelector(`.comment-input[data-post-id="${postId}"]`).value;
    
    if (!content.trim()) return;
    
    const formData = new FormData();
    formData.append('content', content);
    
    fetch(`/comment/${postId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        if (data.success) {
            // Add new comment to DOM
            const commentsContainer = document.querySelector(`.comments-container[data-post-id="${postId}"]`);
            const commentHTML = `
                <div class="comment" id="comment-${data.comment.id}">
                    <strong>${data.comment.user.username}</strong>
                    <span>${data.comment.content}</span>
                    <small>${data.comment.created_at}</small>
                </div>
            `;
            
            if (commentsContainer) {
                commentsContainer.insertAdjacentHTML('beforeend', commentHTML);
            }
            
            // Clear input
            document.querySelector(`.comment-input[data-post-id="${postId}"]`).value = '';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Like buttons
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            likePost(postId);
        });
    });
    
    // Comment buttons
    document.querySelectorAll('.comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            submitComment(postId);
        });
    });
    
    // Comment input enter key
    document.querySelectorAll('.comment-input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const postId = this.getAttribute('data-post-id');
                submitComment(postId);
            }
        });
    });
});
