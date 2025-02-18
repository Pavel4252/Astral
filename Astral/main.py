import speech_recognition as sr
import pyttsx3
import screen_brightness_control as sbc
import os
import sys
import time
import subprocess
import webbrowser
import pyautogui
import openai
from googlesearch import search

# Настройка озвучки
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5

# API-ключ OpenAI (замени на свой)
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

# Контекст общения
conversation_context = []

# Команды и синонимы
COMMANDS = {
    "increase_volume": ["увеличь громкость", "сделай погромче", "повысь звук"],
    "decrease_volume": ["уменьши громкость", "сделай потише", "снизь звук"],
    "increase_brightness": ["увеличь яркость", "добавь света", "повысь яркость"],
    "decrease_brightness": ["уменьши яркость", "сделай темнее", "понизь яркость"],
    "open_browser": ["открой браузер", "запусти google", "запусти интернет"],
    "open_notepad": ["открой блокнот", "запусти текстовый редактор"],
    "search_web": ["найди в интернете", "поиск в google", "погугли"],
    "shutdown": ["выключи компьютер", "заверши работу", "отключи систему"],
    "restart": ["перезагрузи компьютер", "сделай рестарт", "перезагрузи систему"],
    "time": ["сколько времени", "какой сейчас час", "текущее время"],
    "who_are_you": ["как тебя зовут", "кто ты", "представься"],
    "how_are_you": ["как дела", "как ты", "что нового"],
    "exit": ["выход", "закройся", "остановись"],
    "next_slide": ["следующий слайд", "переключи слайд", "покажи следующий слайд", "дальше"],
    "previous_slide": ["предыдущий слайд", "назад", "вернись назад"]
}

# Функция озвучки
def speak(text):
    print(f"Astral: {text}")
    engine.say(text)
    engine.runAndWait()

def open_file_or_app(path):
    try:
        if sys.platform == "win32":
            os.startfile(path)  # Windows
        elif sys.platform == "darwin":
            subprocess.run(["open", path])  # macOS
        else:
            subprocess.run(["xdg-open", path])  # Linux
    except Exception as e:
        print(f"Ошибка: {e}")

# Функция изменения яркости
def change_brightness(amount):
    try:
        if sys.platform == "win32":
            subprocess.run(f"nircmd.exe changebrightness {amount}", shell=True)
        elif sys.platform == "darwin":
            speak("Изменение яркости на MacOS пока не поддерживается.")
        else:  # Linux
            subprocess.run(f"xrandr --output eDP-1 --brightness {amount}", shell=True)
    except Exception as e:
        print(f"Ошибка при изменении яркости: {e}")

# Функция распознавания речи
def listen():
    """Распознавание голосовой команды с обработкой ошибок."""
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.5)
            print("Говорите...")
            audio = recognizer.listen(mic, timeout=10)
            query = recognizer.recognize_google(audio, language='ru-RU').lower()
            print(f"Вы сказали: {query}")
            return query
    except sr.UnknownValueError:
        print("Не удалось распознать речь.")
        return ""
    except sr.RequestError:
        speak("Ошибка подключения к сервису распознавания.")
        return ""
    except Exception as e:
        print(f"Ошибка: {e}")
        return ""

# Анализ команд по ключевым словам
def classify_command(user_input):
    for command, phrases in COMMANDS.items():
        for phrase in phrases:
            if phrase in user_input:
                return command
    return None

# Выполнение команд
def process_command(command, user_input=None):
    if command == "increase_volume":
        pyautogui.press("volumeup", presses=5)
        speak("Громкость увеличена")

    elif command == "decrease_volume":
        pyautogui.press("volumedown", presses=5)
        speak("Громкость уменьшена")

    elif command == "increase_brightness":
        current_brightness = sbc.get_brightness()
        sbc.set_brightness(current_brightness[0] + 25)
        speak("Яркость увеличена")

    elif command == "decrease_brightness":
        current_brightness = sbc.get_brightness()
        sbc.set_brightness(max(0, current_brightness[0] - 25))
        speak("Яркость уменьшена")

    elif command == "open_browser":
        open_file_or_app(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        speak("Открываю браузер")

    elif command == "open_notepad":
        open_file_or_app(r"C:\Windows\notepad.exe")
        speak("Открываю блокнот")

    elif command == "shutdown":
        speak("Вы уверены? Скажите да или нет.")
        confirmation = listen()
        if "да" in confirmation:
            speak("Выключаю компьютер.")
            os.system("shutdown /s /t 5")
        else:
            speak("Отменено")

    elif command == "restart":
        speak("Перезагружаю компьютер.")
        os.system("shutdown /r /t 5")

    elif command == "time":
        current_time = time.strftime("%H:%M")
        speak(f"Сейчас {current_time}")

    elif command == "who_are_you":
        speak("Меня зовут Астрал, я ваш голосовой помощник.")

    elif command == "how_are_you":
        speak("Спасибо, у меня всё хорошо! Как у вас?")

    elif command == "exit":
        speak("Выключаюсь. Хорошего дня!")
        sys.exit()

    elif command == "next_slide":
        pyautogui.press("right")
        speak("Переключаю на следующий слайд.")

    elif command == "previous_slide":
        pyautogui.press("left")
        speak("Возвращаюсь к предыдущему слайду.")

    else:
        speak("Не понял команду.")

# Функция ожидания ключевого слова "Астрал"
def listen_for_keyword():
    while True:
        print("Ожидаю команду")
        keyword = listen()
        if "астрал" in keyword:
            speak("Слушаю вас.")
            listen_for_commands()

# Функция прослушивания команд в течение 17 секунд
def listen_for_commands():
    start_time = time.time()
    while time.time() - start_time < 30:
        command_text = listen()
        if command_text:
            command = classify_command(command_text)
            if command:
                process_command(command, command_text)
            else:
                speak("Не понял команду")
        else:
            print("Команда не распознана.")
    speak("Ожидаю следующую активацию.")

# Запуск бота
if __name__ == "__main__":
    speak("Привет! Я голосовой помощник Astral. Скажите 'Астрал', чтобы активировать меня.")
    listen_for_keyword()
