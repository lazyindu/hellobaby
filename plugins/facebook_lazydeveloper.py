# # ====================================2=====================================




# # import requests
# # import json
# # import subprocess
# # import os

# # output_folder = "Output"
# # # True = keep audio/video files separate and False = keep only the merged file
# # keep_raw_files = False


# # def downloadFile(link, file_name):
# #     headers = {
# #         'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
# #     }
# #     try:
# #         resp = requests.get(link, headers=headers).content
# #     except:
# #         print("Failed to open {}".format(link))
# #         return
# #     with open(os.path.join(output_folder, file_name), 'wb') as f:
# #         f.write(resp)


# # def downloadVideo(link):
# #     headers = {
# #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
# #         'Accept-Language': 'en-US,en;q=0.9',
# #         'Dnt': '1',
# #         'Dpr': '1.3125',
# #         'Priority': 'u=0, i',
# #         'Sec-Ch-Prefers-Color-Scheme': 'dark',
# #         'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
# #         'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="124.0.6367.156", "Google Chrome";v="124.0.6367.156", "Not-A.Brand";v="99.0.0.0"',
# #         'Sec-Ch-Ua-Mobile': '?0',
# #         'Sec-Ch-Ua-Model': '""',
# #         'Sec-Ch-Ua-Platform': '"Windows"',
# #         'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
# #         'Sec-Fetch-Dest': 'document',
# #         'Sec-Fetch-Mode': 'navigate',
# #         'Sec-Fetch-Site': 'none',
# #         'Sec-Fetch-User': '?1',
# #         'Upgrade-Insecure-Requests': '1',
# #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
# #         'Viewport-Width': '1463'
# #     }
# #     try:
# #         resp = requests.get(link, headers=headers)
# #     except:
# #         print("Failed to open {}".format(link))
# #         return
# #     link = resp.url.split('?')[0]
# #     resp = resp.text
# #     splits = link.split('/')
# #     video_id = ''
# #     for ids in splits:
# #         if ids.isdigit():
# #             video_id = ids
# #     try:
# #         target_video_audio_id = resp.split('"id":"{}"'.format(video_id))[1].split(
# #             '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
# #     except:
# #         target_video_audio_id = resp.split('"video_id":"{}"'.format(video_id))[1].split(
# #             '"dash_prefetch_experimental":[')[1].split(']')[0].strip()
# #     list_str = "[{}]".format(target_video_audio_id)
# #     sources = json.loads(list_str)
# #     video_link = resp.split('"representation_id":"{}"'.format(sources[0]))[
# #         1].split('"base_url":"')[1].split('"')[0]
# #     video_link = video_link.replace('\\', '')
# #     print(video_link)
# #     audio_link = resp.split('"representation_id":"{}"'.format(sources[1]))[
# #         1].split('"base_url":"')[1].split('"')[0]
# #     audio_link = audio_link.replace('\\', '')
# #     print(audio_link)
# #     print("Downloading video...")
# #     downloadFile(video_link, 'video.mp4')
# #     print("Downloading audio...")
# #     downloadFile(audio_link, 'audio.mp4')
# #     print("Merging files...")
# #     video_path = os.path.join(output_folder, 'video.mp4')
# #     audio_path = os.path.join(output_folder, 'audio.mp4')
# #     combined_file_path = os.path.join(output_folder, 'merged_final.mp4')
# #     cmd = 'ffmpeg -hide_banner -loglevel error -i "{}" -i "{}" -c copy "{}"'.format(
# #         video_path, audio_path, combined_file_path)
# #     subprocess.call(cmd, shell=True)
# #     os.remove(os.path.join(output_folder, 'video.mp4'))
# #     os.remove(os.path.join(output_folder, 'audio.mp4'))
# #     os.rename(os.path.join(output_folder, 'merged_final.mp4'),
# #               os.path.join(output_folder, '{}.mp4'.format(video_id)))







# # =========================================================================


# # ------------------------------working 1-----------------------------------
# from fdown_api import Fdown
# from os import remove
# from config import FACEBOOK_DURATION_LIMIT
# f = Fdown()
# import os
# from helpo.lazyprogress import progress_for_pyrogram
# import time
# import asyncio
# from plugins.tiktok_x_lazydeveloper import download_video 
# async def getlink(url):
#     link = None
#     try:
#         link = f.get_links(url)
#     except Exception as lazyerror:
#         print(lazyerror)
#     return link

# async def downlaod_vid(url):
#     saved = None
#     try:
#         saved = f.download_video(
#         url,
#         progress_bar=False)
#     except Exception as lazyerror:
#         print(lazyerror)
#     return saved

# async def download_and_send_video(client, message, url):
#     try:
#         # Validate URL
#         if not f.validate_url(url, True):
#             await message.reply("❌ This is not a valid Facebook video link.")
#             return
        
#         x = await message.reply("✅ Valid Facebook video link. Starting download...")

#         # Get video links
#         await asyncio.sleep(1)
#         y = await x.edit_text("<i>⚙Customising link, please wait</i>")
        
        

#         TEMP_DOWNLOAD_FOLDER = f"./downloads/{message.from_user.id}/{time.time()}"
#         if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
#             os.makedirs(TEMP_DOWNLOAD_FOLDER)
#         destination_folder = TEMP_DOWNLOAD_FOLDER


#         # Download video
#         z = await y.edit_text("<i>⚙Downloading video to my server</i> \n⚠NOTE:- This process can take maximum 2 minute")
#         saved_to = await downlaod_vid(video_links)
#         print(f"fdown success_download => {saved_to}")
#         try:
#             format="video"
#             success_download = await download_video(url, destination_folder, message, format)
#             print(f'ytdpl success_download => {success_download}')
#         except Exception as e:
#             print(e)
#             pass

        
#         video_filename = max([os.path.join(destination_folder, f) for f in os.listdir(
#             destination_folder)], key=os.path.getctime)
        
#         # try:
#         #     await message.reply_video(video=open(video_filename, 'rb'))
#         # except Exception as e:
#         #     print(e)
#         #     pass

#         if not saved_to:
#             await message.reply("❌ Failed to download the video. Try again later.")
#             return
        

        
#         # Process and upload
#         thumbnail = f.session.get(video_links.cover_photo).content if video_links.cover_photo else None
#         video_duration = video_links.duration_in_seconds
#         lms = await z.edit_text("<i>⚡ Processing your file to upload...</i>")
#         lst = time.time()
#         try:
#             await client.send_video(
#                     message.chat.id,
#                     video=open(f"{video_filename}","rb"),
#                     # duration=video_duration,
#                     # caption=video_links.title if video_links.title else "Here is your video! 🎥",
                    
#                 )
#         except Exception as err:
#             await message.reply(f"An error occurred while uploading the video: {err}")


#         # await client.send_video(
#         #     message.chat.id,
#         #     open(saved_to, "rb"),
#         #     thumb=thumbnail,
#         #     duration=video_duration,
#         #     caption=video_links.title or "Here is your video! 🎥",
#         #     # progress=progress_for_pyrogram,
#         #     # progress_args=(
#         #     #     "Uploading file",
#         #     #     lms,
#         #     #     lst
#         #     # )
#         # )
#         os.remove(saved_to)
#         await lms.delete()

#     except Exception as e:
#         await message.reply(f"An error occurred: {e}")


# # async def download_and_send_video(client, message, url):
# #     try:
# #         if f.validate_url(message.text, True):
# #             await message.reply("✅ Valid Facebook video link. Starting download...")
# #             await download_and_send_video(client=bot, message=message, url=message.text)
# #         else:
# #             await message.reply("❌ This is not a valid Facebook video link.")
# #     except Exception as e:
# #         await message.reply(f"An error occurred while validating the URL: {e}")
    
# #     #getting url
# #     video_links = await getlink(url)
# #     video_duration = video_links.duration_in_seconds

# #     # waiting for the task to be downloaded
# #     saved_to = await downlaod_vid(video_links)

# #     print(f"saved files to: {saved_to}")

# #     if not saved_to:
# #         await message.reply("❌ Failed to download the video. Try after sometime")
# #         return
# #     # thumbnail = f.session.get(video_links.cover_photo).content
# #     thumbnail = f.session.get(video_links.cover_photo).content if video_links.cover_photo else None
    
# #     lms = await message.reply("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>") 
# #     lst = time.time()
# #     print("Uploading to telegram")
# #     await client.send_video(
# #         message.chat.id,
# #         open(f'{saved_to}', "rb"),
# #         thumb=thumbnail,
# #         duration=video_duration,
# #         caption=video_links.title if video_links.title else "Here is your video! 🎥",
# #         progress=progress_for_pyrogram,
# #         progress_args=(
# #             f"Processing file upload",
# #             lms,
# #             lst
# #         )
# #     )
# #     os.remove(saved_to)
# #     return

# # =======================================================================
