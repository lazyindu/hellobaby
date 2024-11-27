from pyrogram import Client, filters, types
from pyrogram.types import Message
from io import BytesIO
import requests
import time
# from TikTokApi import TikTokApi
import os
# from tiktok_downloader import snaptik
import yt_dlp
import asyncio
import subprocess
from pyrogram import enums
from plugins.utitles import Mdata01
from config import TEL_USERNAME

TELEGRAM_MAX_SIZE_MB = 200
from plugins.ytdl_lazydeveloper import upload_processor
from plugins.ytdl_lazydeveloper import get_metadata
from helpo.lazyprogress import progress_for_pyrogram
# from plugins.functions.display_progress import (
#     progress_for_pyrogram,
#     humanbytes,
#     TimeFormatter,
# )
# def extract_caption_with_ytdlp(url):
#     try:
#         options = {
#             'quiet': True,  # Suppress yt-dlp's output
#             'skip_download': True,  # Don't download the video, only extract metadata
#         }
#         with yt_dlp.YoutubeDL(options) as ydl:
#             info = ydl.extract_info(url, download=False)  # Extract metadata
#             # Extract title or any other metadata
#             title = info.get('title', 'No title available')
#             description = info.get('description', '')
#             return title, description
#     except Exception as e:
#         print(f"Error extracting caption with yt-dlp: {e}")
#         return None, None

import yt_dlp

def extract_caption_with_ytdlp(url):
    try:
        options = {
            'quiet': True,  # Suppress yt-dlp's output
            'skip_download': True,  # Don't download the video, only extract metadata
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)  # Extract metadata
            
            # Extract title and description
            title = info.get('title', 'No title available')
            description = info.get('description', '')

            # Extract the formats (audio or video)
            formats = info.get('formats', [])
            format_type = 'Unknown'

            # Check the formats and determine if it's audio or video
            if formats:
                for fmt in formats:
                    if fmt.get('vcodec') != 'none':  # Video format
                        format_type = 'Video'
                        break
                    elif fmt.get('acodec') != 'none':  # Audio format
                        format_type = 'Audio'
                        break
            print(f"Detected format => {format_type}")   
            return title, description

    except Exception as e:
        print(f"Error extracting caption with yt-dlp: {e}")
        return None, None, None

# Function to handle real-time download progress
# async def download_progress(d, message):
#     if d['status'] == 'downloading':
#         percentage = d.get('downloaded_bytes', 0) / \
#                            d.get('total_bytes', 1) * 100
#         # Update the progress by editing the same message
#         if int(percentage) % 10 == 0:  # Update every 10% to avoid too many edits
#             await message.edit_text(f"Download progress: {percentage:.2f}%")
#     elif d['status'] == 'finished':
#         await message.edit_text("Download complete, processing file...")

def reduce_quality_ffmpeg(video_path, output_path, target_size_mb=50):
    try:
        # Command to reduce video quality using ffmpeg
        command = [
            'ffmpeg', '-i', video_path,
            # Adjust the video bitrate (can be modified as needed)
            '-b:v', '500k',
            '-vf', 'scale=iw/2:ih/2',  # Reduce resolution by half
            '-c:a', 'aac',  # Encode audio with AAC
            '-b:a', '128k',  # Adjust the audio bitrate
            output_path
        ]

        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error reducing video quality with ffmpeg: {e}")
        return False

async def download_video(url, destination_folder, message, format="video"):
    try:
        # Determine the format
        if format == "audio":
            format_type = 'bestaudio/best'
            ext = 'mp3'
        else:
            format_type = 'best'
            ext = 'mp4'

        # yt-dlp configuration with progress_hooks
        
        options = {
            # Use the video ID to avoid filename issues
            'outtmpl': f'{destination_folder}/%(id)s.%(ext)s',
            'format': format_type,  # Select the format based on user input
            'restrictfilenames': True,  # Limit special characters
            'writethumbnail': True,  #for thumbnails
            # Hook to show real-time progress
            # 'progress_hooks': [lambda d: asyncio.create_task(download_progress(d, message))],
        }

        # Download the video or audio
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error during download: {e}")
        return False

async def download_from_lazy_tiktok_and_x(client, message, url):
    try:
        bot_username = client.username if client.username else TEL_USERNAME
        caption_lazy = f"\n\nᴡɪᴛʜ ❤ @{bot_username}"
        
        progress_message2 = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ ᴛᴏ download...</i>")
        
        await asyncio.sleep(1)

        try:
            title, description = extract_caption_with_ytdlp(url)
            print(f"Title => : {title}")
        except Exception as LazyDeveloper:
            print(LazyDeveloper)
            pass

        new_caption = title if title else " "
        while len(new_caption) + len(caption_lazy) > 1024:
            new_caption = new_caption[:-1]  # Trim caption if it's too long
        new_caption = new_caption + caption_lazy  # Add bot username at the end
        # Initialize media list
    
        format = "video"
        TEMP_DOWNLOAD_FOLDER = f"./downloads/{message.from_user.id}/{time.time()}"
        if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
            os.makedirs(TEMP_DOWNLOAD_FOLDER)
        # Using the temporary download folder
        destination_folder = TEMP_DOWNLOAD_FOLDER  

        # Start the download and update the same message
        success_download = await download_video(url, destination_folder, progress_message2, format)
        # print(f"Download success")
        if not success_download:
            await progress_message2.edit_text('Error during the video download. Please try again later.')
            return

        # Get the name of the downloaded file
        video_filename = max([os.path.join(destination_folder, f) for f in os.listdir(
            destination_folder)], key=os.path.getctime)
        # print(f"video filename:{video_filename}")

        # Check the file size
        file_size_mb = os.path.getsize(video_filename) / (1024 * 1024)
        if file_size_mb > TELEGRAM_MAX_SIZE_MB:
            lzz = await message.reply_text(f'The file is too large ({file_size_mb:.2f} MB). '
                                    f'Reducing the quality to meet the  limit...')

            # Attempt to reduce the quality using ffmpeg
            output_filename = os.path.join(
                destination_folder, 'compressed_' + os.path.basename(video_filename))
            success_reduce = reduce_quality_ffmpeg(
                video_filename, output_filename, TELEGRAM_MAX_SIZE_MB)

            if not success_reduce:
                await lzz.edit_text('Error reducing the video quality. Please try again later.')
                return
            await lzz.delete()


            # Switch to the compressed file for sending
            video_filename = output_filename

        # Send the video/audio file to the user
        progress_message3 = await progress_message2.edit_text("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>")
        # await asyncio.sleep(1)
        

        try:
            # await upload_processor(client, message, url, video_filename)
            width, height, duration = await Mdata01(video_filename)
            
            await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)

            # print(f"w->{width}--h->{height}--d->{duration}")
            start_time = time.time()
            await client.send_video(
                    chat_id=message.chat.id,
                    video=open(video_filename, 'rb'),
                    caption=new_caption,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    parse_mode=enums.ParseMode.HTML,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<blockquote>🍟Upload Your video...</blockquote>============x============<blockquote>{new_caption}</blockquote>",
                        progress_message3,
                        start_time,
                    ))
        except Exception as e:
            await client.send_message(message.chat.id, f'Error sending the file: {e}')
            print(f"Error sending the file: {e}")
        finally:
            # Delete the downloaded file (optional)
            if os.path.exists(video_filename):
                os.remove(video_filename)

        await progress_message3.delete()
        lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
        await asyncio.sleep(100)
        await lazydeveloper.delete()
    except Exception as e:
        await message.reply(f"❌ An unexpected error occurred: {e}")
