import logging
import tempfile
import yt_dlp as ytdl
import os
from pyrogram import Client, types
from pyrogram.enums import ChatAction

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to download the video
def ytdl_download(url: str, tempdir: str, bm) -> list:
    chat_id = bm.chat.id
    DOWNLOAD_LOCATION = tempdir  # Use the temporary directory

    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    # yt-dlp options
    ydl_opts = {
        "progress_hooks": [lambda d: download_hook(d, bm)],  # Call download_hook to show download progress
        "outtmpl": os.path.join(DOWNLOAD_LOCATION, "%(title).70s.%(ext)s"),  # Set output template
        "restrictfilenames": False,
        "quiet": True,
    }

    # Download the video using yt-dlp
    try:
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Download video from URL
        video_paths = list(os.path.join(DOWNLOAD_LOCATION, f) for f in os.listdir(DOWNLOAD_LOCATION))
        return video_paths
    except Exception as e:
        logging.error("Download failed: %s", e)
        return []

# Hook function to show progress
async def download_hook(d, bm):
    if d['status'] == 'downloading':
        progress = d['downloaded_bytes'] / d['total_bytes'] * 100
        await bm.edit_text(f"Downloading: {progress:.2f}%")
    elif d['status'] == 'finished':
        await bm.edit_text("Download complete! Sending now...")

# Main function to handle the bot and download request
async def download_from_youtube(client: Client, message: types.Message, url: str):
    # Temporary directory to store the video
    temp_dir = tempfile.TemporaryDirectory(prefix="ytdl-", dir="./")

    # Download the video
    video_paths = ytdl_download(url, temp_dir.name, message)
    
    if video_paths:
        # Video download complete, now upload it to Telegram
        logging.info("Download complete. Sending the video.")
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        video_path = video_paths[0]  # Get the downloaded video file path
        await client.send_video(message.chat.id, video_path, caption="Here is your video!")
        temp_dir.cleanup()  # Cleanup temporary directory after sending the file
    else:
        # If download failed
        await message.reply_text("Failed to download the video. Please try again.")

# Setting up the Telegram Bot
@Client.on_message()
async def handle_message(client: Client, message: types.Message):
    if message.text:
        url = message.text.strip()
        if "youtube.com" in url or "youtu.be" in url:  # Check if it's a YouTube link
            await download_from_youtube(client, message, url)
        else:
            await message.reply_text("Please send a valid YouTube URL.")


