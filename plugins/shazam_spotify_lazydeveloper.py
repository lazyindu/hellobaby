# import os
# import re
# import requests
# from aiogram import types
# from aiogram.types import InputFile
# from shazamio import Shazam

# # Assuming these are imported from your actual code
# # from your_module import FastDLAppDownloader, shazamtop, SearchFromSpotify, DownloadMusic

# async def ShazamIO(video_path:str):
# 	shazam = Shazam()
# 	out = await shazam.recognize_song(video_path)
# 	return out



# async def shazam_spotify(message: types.Message):
#     text = message.text
#     if re.search(instagram_regex, text):
#         msg_del = await message.reply("⏳ Downloading...")
#         app = FastDLAppDownloader()

#         # Get video download link from FastDLApp
#         vid_url = app.download_url(text)

#         if vid_url:
#             try:
#                 # Download the video
#                 video_path = await download_video(vid_url, message.message_id)

#                 # Send the downloaded video to user
#                 await msg_del.delete()
#                 input_file = InputFile(video_path)
#                 await bot.send_document(message.chat.id, input_file, caption="Downloaded via @Ultimatedownbot")

#                 # Use Shazam to identify the music
#                 shazammusic = await shazamtop(video_path)
#                 title = shazammusic.get('title')

#                 if title:
#                     # Search for the music on Spotify
#                     musics = SearchFromSpotify(track_name=title, limit=5)
#                     audio_urls = DownloadMusic(musics)
#                     # You can send the audio URLs or process them as needed

#                 # Clean up video file after processing
#                 os.remove(video_path)

#             except Exception as err:
#                 # Handle error: if anything goes wrong
#                 await msg_del.delete()
#                 await message.reply(f"Error: {err}")

#                 # Clean up in case of error
#                 if os.path.exists(video_path):
#                     os.remove(video_path)

#             finally:
#                 # Ensure that the video is deleted after processing
#                 if os.path.exists(video_path):
#                     os.remove(video_path)
