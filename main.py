import telebot
import os
from telebot import types
import yt_dlp

my_secret = os.environ['B']
bot_token = os.getenv('B')
bot = telebot.TeleBot(bot_token)

# Initialize a dictionary to store the YouTube link for each user
user_data = {}

def download_video_from_youtube(link):
    ydl_opts = {'format': 'best', 'outtmpl': 'video.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
    filename = 'video.' + info['ext']
    title = info['title']
    return filename, title

def download_audio_from_youtube(link):
    ydl_opts = {'format': 'bestaudio', 'outtmpl': 'audio.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
    filename = 'audio.' + info['ext']
    title = info['title']
    return filename, title

@bot.message_handler(func=lambda msg: msg.text.startswith('http'))
def process_url(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Download Video", callback_data='video')
    item2 = types.InlineKeyboardButton("Download Audio", callback_data='audio')
    markup.add(item1, item2)

    user_data[message.chat.id] = message.text  # Store the link in user's data
    bot.send_message(message.chat.id, "Select download type:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        link = user_data[call.message.chat.id]  # Retrieve the link
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Starting download, please wait...')
        if call.data == 'video':
            filename, title = download_video_from_youtube(link)
            video = open(filename, 'rb')
            bot.send_video(call.message.chat.id, video, caption=f'{title}\nVideo downloaded by Bot')
            video.close()
            os.remove(filename)  # delete the file after sending it
        elif call.data == 'audio':
            filename, title = download_audio_from_youtube(link)
            audio = open(filename, 'rb')
            bot.send_audio(call.message.chat.id, audio, caption=f'{title}\nAudio downloaded by Bot')
            audio.close()
            os.remove(filename)  # delete the file after sending it
    except Exception as e:
      print(e)  # print the actual error message
      bot.edit_message_text(chat_id=call.message.chat.id,     
      message_id=call.message.message_id, text='Failed to download. Please try again with a different link.')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحبًا، يرجى إرسال رابط YouTube واختر ما إذا كنت ترغب في تنزيل الفيديو أو الصوت. \n\n Hello, please send a YouTube link and choose whether you want to download video or audio.")

bot.polling()
