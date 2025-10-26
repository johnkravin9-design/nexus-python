import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Replace the video import and handling
old_import = "from video_utils import save_video_file, VideoProcessor"
new_import = """try:
    from video_utils import save_video_file, VideoProcessor, save_video_file_fallback
    VIDEO_SUPPORT = True
except ImportError:
    VIDEO_SUPPORT = False
    print("Video support disabled - required dependencies not installed")"""

content = content.replace(old_import, new_import)

# Update the video handling in create_post route
old_video_code = """        # Handle video upload
        elif video and VideoProcessor.allowed_video_file(video.filename):
            result = save_video_file(video, session['username'], app)
            if result['success']:
                new_post.video_url = result['video_url']
                new_post.video_thumbnail = result['thumbnail_url']
                new_post.video_duration = result['duration']
                new_post.media_type = 'video'
            else:
                flash('Error processing video file', 'error')
                return render_template('create_post.html')"""

new_video_code = """        # Handle video upload
        elif video and VIDEO_SUPPORT and VideoProcessor.allowed_video_file(video.filename):
            try:
                result = save_video_file(video, session['username'], app)
                if not result['success']:
                    # Fallback to simple video saving
                    result = save_video_file_fallback(video, session['username'], app)
            except Exception as e:
                print(f"Video processing error: {e}")
                result = save_video_file_fallback(video, session['username'], app)
            
            if result['success']:
                new_post.video_url = result['video_url']
                new_post.video_thumbnail = result['thumbnail_url']
                new_post.video_duration = result['duration']
                new_post.media_type = 'video'
            else:
                flash('Error processing video file', 'error')
                return render_template('create_post.html')
        elif video and not VIDEO_SUPPORT:
            flash('Video upload is currently not supported on this server', 'error')
            return render_template('create_post.html')"""

content = content.replace(old_video_code, new_video_code)

# Write the updated content back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated app.py to handle missing video dependencies")
