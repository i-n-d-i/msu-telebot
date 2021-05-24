import numpy as np # generate random
import os          # get current directory path
import subprocess  # execute ffmpeg
import telebot     # run telegram bot

from datetime import datetime # generate log

users_tasks = dict()
bot = telebot.TeleBot('1197461609:AAHfP9oRXvyZDyjEpDQ92JfIdkOqVFJWK2A')
root = os.getcwd() + "/dataset/"


def save_ogg(ogg_data, ogg_path):
    with open(ogg_path, "wb") as file:
        file.write(ogg_data)


def convert_ogg_wav(ogg_path, dst_path):
    rate = 48000
    cmd = f"ffmpeg -i {ogg_path} -ar {rate} {dst_path} -y -loglevel panic"
    log(cmd)
    with subprocess.Popen(cmd.split()) as p:
        try:
            p.wait(timeout=2)
        except:
            p.kill()
            p.wait()
            return "timeout"


def generate_task():
    return ' '.join(list(map(str, np.random.randint(10, size=5))))


def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + " " + text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user = message.from_user.id
    text = message.text
    log(f"User ({user}): {text}")

    users_tasks[user] = generate_task()
    bot.send_message(user,
        f"Пожалуйста назовите следующие 5 цифры с паузами:\n{users_tasks[user]}")


@bot.message_handler(content_types=['voice'])
def get_voice_messages(message):
    user = message.from_user.id
    voice = message.voice
    if user not in users_tasks:
        bot.send_message(user, "/start")
    log(f"User ({user}): voice")

    tele_file = bot.get_file(voice.file_id)
    ogg_data = bot.download_file(tele_file.file_path)
    file_name = users_tasks[user].replace(" ", "_")
    ogg_path = root + "/ogg/" + file_name + ".ogg"
    wav_path = root + "/wav/" + file_name + ".wav"
    save_ogg(ogg_data, ogg_path)
    convert_ogg_wav(ogg_path, wav_path)
    bot.send_message(user, "Спасибо")


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)

