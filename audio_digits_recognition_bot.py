import numpy as np # generate random
import os          # get current directory path
import subprocess  # execute ffmpeg
import telebot     # run telegram bot

from datetime import datetime # generate log
from split_by_vad import sec2samples, get_segments_energy, get_vad_mask, mask_compress  

from scipy.io.wavfile import read, write
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

import librosa
import pickle


#@audio_digits_dataset_bot
bot = telebot.TeleBot('1211712111:AAEcF-rwu43Ea1V7KM3DCj_-F9KAFCJDEJE')
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

def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + " " + text)

def vad(wav_file_path):
    segment_duration = 0.1
    vad_threshold = 0.01
    sample_rate, audio = read(wav_file_path)

    ## todo
    segment_duration_samples = sec2samples(segment_duration, sample_rate)
    segments_energy = get_segments_energy(audio, segment_duration_samples)
    vad_mask = get_vad_mask(segments_energy, vad_threshold)
    segments = mask_compress(vad_mask)

    print(len(segments))
    assert 1 == len(segments), "Bad threshold"
    
    max_duration = 0
    for segment in segments:
        duration = (segment.stop - segment.start) * segment_duration_samples / sample_rate
        if duration > max_duration:
            max_duration = duration
    assert max_duration <= 0.6, f"max_duration={max_duration:.3f}"
    
    wav_path_after_vad = root + "inference.wav"
    start = segments[0].start * segment_duration_samples
    stop = segments[0].stop * segment_duration_samples
    write(wav_path_after_vad, sample_rate, audio[start:stop])
    return wav_path_after_vad

def predict(wav_path_after_vad):
    filename = "model.pkl"
    with open(filename, 'rb') as f:
        model_pickled = f.read()
    model = pickle.loads(model_pickled)
    

    sample_rate, audio = read(wav_path_after_vad)
    max_duration_sec = 0.6
    max_duration = int(max_duration_sec * sample_rate + 1e-6)
    if len(audio) < max_duration:
        audio = np.pad(audio, (0, max_duration - len(audio)), constant_values=0)
    feature = librosa.feature.melspectrogram(audio.astype(float), sample_rate, n_mels=16, fmax=1000)
    features_flatten = feature.reshape(-1)
    answer = model.predict([features_flatten])[0]
    return answer

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user = message.from_user.id
    text = message.text
    log(f"User ({user}): {text}")

    bot.send_message(user,
        f"Пожалуйста отправьте голосовое сообщение с цифрой. И я попробую её отгадать :)")

@bot.message_handler(content_types=['voice'])
def get_voice_messages(message):
    user = message.from_user.id
    voice = message.voice
    log(f"User ({user}): voice")

    tele_file = bot.get_file(voice.file_id)
    ogg_data = bot.download_file(tele_file.file_path)
    file_name = "inference_file" # need to generate uniq name
    ogg_path = root + "/ogg/" + file_name + ".ogg"
    wav_path = root + "/wav/" + file_name + ".wav"
    save_ogg(ogg_data, ogg_path)
    convert_ogg_wav(ogg_path, wav_path)
    # ... todo
    wav_path_after_vad = vad(wav_path)
    answer = predict(wav_path_after_vad)
    bot.send_message(user, "Спасибо, вы назвали цифру - " + str(answer) + ". Извините, если я не угадал. Попробуйте еще раз :)")


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)

