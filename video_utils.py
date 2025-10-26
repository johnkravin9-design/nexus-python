import os
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import subprocess

class VideoProcessor:
    @staticmethod
    def allowed_video_file(filename):
        ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def generate_thumbnail(video_path, thumbnail_path):
        """Generate thumbnail from video using ffmpeg"""
        try:
            # Use ffmpeg to capture frame at 1 second
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:01',  # Capture at 1 second
                '-vframes', '1',    # Capture 1 frame
                '-q:v', '2',        # Quality
                thumbnail_path,
                '-y'  # Overwrite output file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            # Create a default thumbnail
            default_thumb = Image.new('RGB', (320, 180), color='#333333')
            default_thumb.save(thumbnail_path)
            return True
    
    @staticmethod
    def get_video_duration(video_path):
        """Get video duration using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return int(duration)
        except Exception as e:
            print(f"Error getting video duration: {e}")
        return 0  # Default duration if cannot determine
    
    @staticmethod
    def compress_video(input_path, output_path, target_size_mb=50):
        """Compress video to target size"""
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vcodec', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-acodec', 'aac',
                '-b:a', '128k',
                output_path,
                '-y'
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"Error compressing video: {e}")
            return False

def save_video_file(file, username, app):
    """Save video file and generate thumbnail"""
    if file and VideoProcessor.allowed_video_file(file.filename):
        # Create unique filename
        timestamp = int(datetime.utcnow().timestamp())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"video_{username}_{timestamp}.{file_ext}"
        
        # Create directories
        videos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Save video file
        video_path = os.path.join(videos_dir, unique_filename)
        file.save(video_path)
        
        # Generate thumbnail
        thumbnail_filename = f"thumb_{username}_{timestamp}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        
        thumbnail_generated = VideoProcessor.generate_thumbnail(video_path, thumbnail_path)
        
        # Get video duration
        duration = VideoProcessor.get_video_duration(video_path)
        
        return {
            'video_url': f"uploads/videos/{unique_filename}",
            'thumbnail_url': f"uploads/thumbnails/{thumbnail_filename}",
            'duration': duration,
            'success': True
        }
    
    return {'success': False, 'error': 'Invalid video file'}

# Fallback function if ffmpeg is not available
def save_video_file_fallback(file, username, app):
    """Fallback video saving without ffmpeg"""
    if file and VideoProcessor.allowed_video_file(file.filename):
        timestamp = int(datetime.utcnow().timestamp())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"video_{username}_{timestamp}.{file_ext}"
        
        videos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        thumbnails_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Save video file
        video_path = os.path.join(videos_dir, unique_filename)
        file.save(video_path)
        
        # Create a simple colored thumbnail
        thumbnail_filename = f"thumb_{username}_{timestamp}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
        
        # Create a default video thumbnail
        thumb = Image.new('RGB', (320, 180), color='#4F46E5')  # Purple background
        thumb.save(thumbnail_path)
        
        # Add a play icon (simplified)
        try:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(thumb)
            # Draw a simple play triangle
            draw.polygon([(140, 70), (140, 110), (180, 90)], fill='white')
            thumb.save(thumbnail_path)
        except:
            pass
        
        return {
            'video_url': f"uploads/videos/{unique_filename}",
            'thumbnail_url': f"uploads/thumbnails/{thumbnail_filename}",
            'duration': 0,  # Unknown duration
            'success': True
        }
    
    return {'success': False, 'error': 'Invalid video file'}
