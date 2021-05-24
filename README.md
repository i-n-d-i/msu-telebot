## Semester work - telebot

### The second part of the work in fourth semester included:
* dataset bot
* recognition bot

### Folder structure requirements:
```
dataset
-ogg
-wav
-splitted
--0
--1
--2
--3
--4
--5
--6
--7
--8
--9
```

### Dataset bot
The `audio_digits_dataset_bot.py` program - is a bot that will help you create a your own dataset of audio.

#### To check the work of these program you need:
* download all using command `git clone https://github.com/i-n-d-i/telebot`
* create your own bot in Telegram using `BotFather`
* BotFather will give you the ID of your bot and you should insert your ID on the 9th line of code: `bot = telebot.TeleBot('...')`
* run program using command `python3 audio_digits_dataset_bot.py`
* then you need to record as much audio as possible for your dataset, they will be saved in folders `ogg` and `wav`.

### Split audio
Now you need to split your audios into pieces using the program `split_by_vad.py`

#### To check the work of these program you need:
* run program using command `python3 split_by_vad.py dataset/wav/audio_name.wav 0.1 0.01 dataset/splitted/`
* audio files will be saved in folders, located in `splitted`

Now you have a certain number of audio files with numbers from 0 to 9

### Recognition bot
The `audio_digits_recognition_bot.py` program - is a bot that receives from you an audio message with a number and guesses what number you called.

#### To check the work of these program you need:
* run program `model.py` using command `python3 model.py` - this program will train your model and create a file `model.pkl` that is useful for the bot.
* create your own bot in Telegram using `BotFather`
* BotFather will give you the ID of your bot and you should insert your ID on the 18th line of code: `bot = telebot.TeleBot('...')`
* run program using command `python3 audio_digits_recognition_bot.py`

#### If you did  all these steps correctly, now you can use your bot :) Good luck!



 
