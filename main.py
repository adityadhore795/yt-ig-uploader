import os
import yt_dlp
import dropbox
import shutil

# === CONFIG ===
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@Knot_Master/shorts"
DROPBOX_UPLOAD_PATH = "/knotmaster/"
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
UPLOADED_IDS_FILE = "uploaded_ids.txt"

APP_KEY = "kl4k2jflpzj9xbl"
APP_SECRET = "w5ecc19bvvz6jso"
REFRESH_TOKEN = "-V1J74QHCs8AAAAAAAAAAbwh7YXd-HIlQOlxmwL0672zAKqeuYNVNrLd3Vgtye0g"

HASHTAGS = "#crafts"

# === INIT DROPBOX CLIENT ===
dbx = dropbox.Dropbox(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    oauth2_refresh_token=REFRESH_TOKEN
)

# === LOAD ALREADY UPLOADED VIDEO IDS ===
if os.path.exists(UPLOADED_IDS_FILE):
    with open(UPLOADED_IDS_FILE, "r") as f:
        uploaded_ids = set(line.strip() for line in f)
else:
    uploaded_ids = set()

# === FETCH VIDEO LIST FROM CHANNEL ===
ydl_opts = {
    'quiet': True,
    'extract_flat': True,
    'force_generic_extractor': False
}

with yt_dlp.YoutubeDL(ydl_opts) as yt_dl:
    result = yt_dl.extract_info(YOUTUBE_CHANNEL_URL, download=False)
    entries = result['entries']

# === CHECK EACH VIDEO UNTIL WE FIND AN UNSEEN ONE ===
for entry in entries:
    video_id = entry['id']
    if video_id in uploaded_ids:
        print(f"🚫 Video {video_id} already uploaded. Skipping.")
        continue

    video_url = entry['url']
    print("✅ Found new video:", video_url)

    # === DOWNLOAD THE NEW VIDEO ===
    ydl_opts_download = {
        'cookiefile': 'cookies.txt',
        'format': 'best[ext=mp4]/best',
    }

    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        info = ydl.extract_info(video_url, download=True)

    downloaded_filename = ydl.prepare_filename(info)
    shutil.move(downloaded_filename, "latest_short.mp4")

    title = info.get('title', '').strip().replace('\n', ' ')
    description = info.get('description', '').strip().replace('\n', ' ')
    video_filename = "latest_short.mp4"

    # === CLEAN FILENAME ===
    def clean(text):
        return "".join(c for c in text if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')[:50]

    final_filename = f"{clean(title)}__{clean(description)}__{clean(HASHTAGS)}.mp4"

    # === UPLOAD TO DROPBOX ===
    with open(video_filename, "rb") as f:
        dbx.files_upload(f.read(), DROPBOX_UPLOAD_PATH + final_filename, mode=dropbox.files.WriteMode("overwrite"))

    print("✅ Uploaded to Dropbox as:", final_filename)

    # === DELETE OLD FILES (Keep only the latest 8) ===
    folder_path = "/knotmaster/"
    res = dbx.files_list_folder(folder_path)
    sorted_files = sorted(res.entries, key=lambda x: x.server_modified, reverse=True)

    for file in sorted_files[8:]:
        dbx.files_delete_v2(file.path_lower)
        print("🗑️ Deleted old file:", file.name)

    # === LOG VIDEO ID AS UPLOADED ===
    with open(UPLOADED_IDS_FILE, "a") as f:
        f.write(video_id + "\n")

    break  # Stop after uploading one new video
