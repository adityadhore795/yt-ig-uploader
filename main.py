import os
import yt_dlp

# Debugging cookies.txt location
cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
print("🔍 Looking for cookies.txt at:", cookie_path)
print("📂 File exists?", os.path.exists(cookie_path))

video_url = "https://www.youtube.com/shorts/4s-C3NvIfKM"

# yt-dlp options
ydl_opts_download = {
    'format': 'mp4',
    'outtmpl': 'video.mp4',
    'cookies': cookie_path,
    'quiet': False,
    'no_warnings': True,
}

# Run the download
with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
    print(f"✅ Trying to download: {video_url}")
    info = ydl.extract_info(video_url, download=True)
    print("🎉 Download complete!")

