# from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
# from pyrogram import Client, filters
# from pyrogram.enums import ParseMode
# import re
# # from pytube import YouTube, Playlist
# from helpo.youtube import get_youtube_video_id


# async def handle_youtube_link(bot, message, url):
#     try:
#         video_id = get_youtube_video_id(url)
#         youtube = YouTube(f'https://www.youtube.com/watch?v={video_id}')
#         thumbnail_url = youtube.thumbnail_url
#         title = youtube.title
#         description = youtube.description
#         formatted_text = (
#             f"<b>{title}</b>\n\n"
#             f"{description[:300]}{'...' if len(description) > 300 else ''} "
#             f"<a href='https://www.youtube.com/watch?v={video_id}'>Read more</a>\n\n"
#             "Please ensure you have the rights to download this content."
#         )

#         resolutions = [stream.resolution for stream in youtube.streams.filter(progressive=True)]

#         # Generate buttons
#         buttons = [
#             InlineKeyboardButton(text=resolution, callback_data=f"res_{video_id}:{resolution}")
#             for resolution in resolutions
#         ]
#         t_buttons = [
#             InlineKeyboardButton(text="Video", callback_data=f"type_{video_id}:video"),
#             InlineKeyboardButton(text="Audio", callback_data=f"type_{video_id}:audio")
#         ]
#         d_buttons = [
#             InlineKeyboardButton(text="Download", callback_data=f"download_{video_id}:n:n")
#         ]
#         keyboard = [buttons, t_buttons, d_buttons]

#         # Send response
#         markup = InlineKeyboardMarkup(keyboard)
#         await message.reply_photo(
#             photo=thumbnail_url,
#             caption=formatted_text,
#             parse_mode="HTML",
#             reply_markup=markup
#         )
#     except Exception as e:
#         await bot.send_message(message.chat.id, f"Error: {e}")

# async def handle_youtube_playlist_link(bot, message, url):
#     try:
#         playlist = Playlist(url)
#         playlist_title = playlist.title

#         formatted_text = (
#             f"<b>Playlist: {playlist_title}</b>\n\n"
#             "Please ensure you have the rights to download this content."
#         )

#         resolutions = ['360p', '480p', '720p']
#         buttons = [
#             InlineKeyboardButton(text=resolution, callback_data=f"pl_res_{playlist.playlist_id}:{resolution}")
#             for resolution in resolutions
#         ]
#         t_buttons = [
#             InlineKeyboardButton(text="Video", callback_data=f"pl_type_{playlist.playlist_id}:video"),
#             InlineKeyboardButton(text="Audio", callback_data=f"pl_type_{playlist.playlist_id}:audio")
#         ]
#         d_buttons = [
#             InlineKeyboardButton(text="Download", callback_data=f"pl_download_{playlist.playlist_id}:n:n")
#         ]
#         keyboard = [buttons, t_buttons, d_buttons]

#         # Send response
#         markup = InlineKeyboardMarkup(keyboard)
#         await bot.send_message(chat_id=message.chat.id, text=formatted_text, reply_markup=markup)
#     except Exception as e:
#         await bot.send_message(message.chat.id, f"Error: {e}")

# async def download_youtube_video(client, message, url):
#     try:
#         video_regex = r'https?:\/\/(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})$'
#         playlist_regex = r"(?:(?:https?:)?//)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)"

#         # Match URL
#         video_match = re.match(video_regex, url)
#         playlist_match = re.match(playlist_regex, url)

#         # Handle matches
#         if video_match:
#             await handle_youtube_link(client, message, url)
#         elif playlist_match:
#             await handle_youtube_playlist_link(client, message, url)
#         else:
#             await client.send_message(message.chat.id, "Invalid YouTube link. Please send a valid video or playlist URL.")
#     except Exception as lazyerror:
#         print(lazyerror)

# =========================================================================
# =========================================================================
# =========================================================================
# =========================================================================

# async def handle_youtube_link(bot, message, url):
#     video_id = get_youtube_video_id(url)
#     youtube = YouTube(f'https://www.youtube.com/watch?v={video_id}')
#     thumbnail_url = youtube.thumbnail_url
#     title = youtube.title
#     description = youtube.description
#     formatted_text = f"<b>{title}</b>\n\n{description[:300]}{'...' if len(description) > 300 else ''} <a href='https://www.youtube.com/watch?v={video_id}''>Read more</a>\n\n\nOnly download videos that you have the right to download. Do not use this bot to download copyrighted content that you do not have permission to use.\nDo not use this bot to download content that is illegal or violates Telegram's terms of service.\nBe respectful to other users and do not use the bot to spam or harass others.\nThe bot can only download videos that are publicly available on YouTube.\nThe bot can only download videos up to a maximum file size of 2 GB.\nThe bot can only download videos that are available in a format that can be downloaded."
#     resolutions = []

#     try:
#         for stream in youtube.streams.filter(progressive=True):
#             resolutions.append(stream.resolution)
#         buttons = [
#             InlineKeyboardButton(text=resolution, callback_data=f"res_{video_id}:{resolution}") for resolution in resolutions
#         ]
#         # add two new buttons for 'video' and 'audio' in a new row
#         t_buttons = []

#         t_buttons.append(InlineKeyboardButton(
#             text="Video", callback_data=f"type_{video_id}:video"))
#         t_buttons.append(InlineKeyboardButton(
#             text="Audio", callback_data=f"type_{video_id}:audio"))

#         # add a 'download' button in another new row
#         d_buttons = [InlineKeyboardButton(
#             text="Download", callback_data=f"download_{video_id}:n:n")]
#         keyboard = [buttons, t_buttons, d_buttons]
#         markup = InlineKeyboardMarkup(keyboard)
#         await message.reply_photo(
#             photo=thumbnail_url,
#             caption=formatted_text,
#             parse_mode=ParseMode.HTML,
#             reply_markup=markup)
#     except Exception as e:
#         await bot.send_message(message.chat.id, f"Error: {e}")

# async def handle_youtube_playlist_link(bot, message, url):
#     try:
#         playlist_url = url
#         chat_id = message.chat.id
#         match = re.search(r"list=([A-Za-z0-9_-]+)", playlist_url)
#         if match:
#             playlist_id = match.group(1)
#         else:
#             return await bot.send_message(chat_id, 'Something went wrong; Youtube Link Not Found!')

#         playlist = Playlist(playlist_url)
#         playlist_title = playlist.title

#         formatted_text = f"<b>Playlist: {playlist_title}</b>\n\nOnly download videos that you have the right to download. Do not use this bot to download copyrighted content that you do not have permission to use.\nDo not use this bot to download content that is illegal or violates Telegram's terms of service.\nBe respectful to other users and do not use the bot to spam or harass others.\nThe bot can only download videos that are publicly available on YouTube.\nThe bot can only download videos up to a maximum file size of 2 GB.\nThe bot can only download videos that are available in a format that can be downloaded."

#         resolutions = ['360p', '480p', '720p']
#         buttons = [
#             InlineKeyboardButton(text=resolution, callback_data=f"pl_res_{playlist_id}:{resolution}") for resolution in resolutions
#         ]

#         t_buttons = []
#         t_buttons.append(InlineKeyboardButton(
#             text="Video", callback_data=f"pl_type_{playlist_id}:video"))
#         t_buttons.append(InlineKeyboardButton(
#             text="Audio", callback_data=f"pl_type_{playlist_id}:audio"))

#         d_buttons = [InlineKeyboardButton(
#             text="Download", callback_data=f"pl_download_{playlist_id}:n:n")]

#         keyboard = [buttons, t_buttons, d_buttons]
#         markup = InlineKeyboardMarkup(keyboard)

#         await bot.send_message(chat_id=chat_id, text=formatted_text ,reply_markup=markup)

#     except Exception as e:
#         await bot.send_message(message.chat.id, f"Error: {e}")

# async def download_youtube_video(client, message, url):
#     video_regex = r'https?:\/\/(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})$'
#     playlist_regex = r"(?:(?:https?:)?//)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)"

#     # match url
#     video_match = re.match(video_regex, url)
#     playlist_match = re.match(playlist_regex, url)

#     # proceed match
#     if video_match:
#         await handle_youtube_link(client, message, url)
#         print(f"handle_youtube_link")
#     elif playlist_match:
#         await handle_youtube_playlist_link(client, message, url)
#         print(f"handle_youtube_playlist_link")


