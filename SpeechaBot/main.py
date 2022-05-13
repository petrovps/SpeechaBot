import telebot
import requests
import speech_recognition as sr
import moviepy.editor as mp
from pydub import AudioSegment
import os
import config

bot = telebot.TeleBot(config.token)
r = sr.Recognizer()
audio_folder = os.path.join(os.getcwd(), 'audio')
video_folder = os.path.join(os.getcwd(), 'video')


"""# TO DO: 
    Add function for set up language for users 
    Add OCR for image recognition
"""

@bot.message_handler(commands=["start", "help"])
def start_processing(message):
    text = ("I translate audio and video messages into text.\n"+
            "You can add me to chat with voice messages lovers\n"+
            "and enjoy the text version\n"+
            "(don't forget to give me permission to read messages)\n")
    bot.reply_to(message, text)

@bot.message_handler(content_types=['voice'])
def audio_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    file_name = file_info.file_path.split('/')[1]
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
    audio = audio_converter(file_name, file)
    response = text_recognition(audio)
    empty_folders()
    bot.reply_to(message, response)

@bot.message_handler(content_types=['video_note'])
def videomessage_processing(message):
    file_info = bot.get_file(message.video_note.file_id)
    file_name = file_info.file_path.split('/')[1]
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path))
    audio = video_converter(file_name, file)
    response = text_recognition(audio)
    empty_folders()
    bot.reply_to(message, response)

def audio_converter(file_name, file):
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    path_ogg = os.path.join(audio_folder, f"{file_name}.ogg")
    path_wav = os.path.join(audio_folder, f"{file_name}.wav")
    with open(path_ogg, 'wb') as f:
        f.write(file.content)
    sound = AudioSegment.from_ogg(path_ogg)
    sound.export(path_wav, format="wav")
    return path_wav

def video_converter(file_name, file):
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    path_mp4 = os.path.join(video_folder, f"{file_name}.mp4")
    path_wav = os.path.join(audio_folder, f"{file_name}.wav")
    with open(path_mp4, 'wb') as f:
        f.write(file.content)
    clip = mp.VideoFileClip(path_mp4)
    clip.audio.write_audiofile(path_wav)
    return path_wav

def empty_folders():
    for filename in os.listdir(audio_folder):
        file_path = os.path.join(audio_folder, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    for filename in os.listdir(video_folder):
        file_path = os.path.join(video_folder, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

def text_recognition(audio):
    with sr.AudioFile(audio) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data,language='ru_RU')
        except sr.UnknownValueError:
            text = "непонятно)"
        return text


if __name__ == '__main__':
    while True:
        try:
            bot.polling(2)
        except Exception as error:
            print(error)