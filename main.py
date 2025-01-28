from telegram.ext import ApplicationBuilder
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import schedule
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

t = Thread(target=run)
t.start()
# Настройки
BOT_TOKEN = "7537671678:AAFRy3uRWrP_cQkoR5_XVeEceDtz_tbILoo"  # Вставь сюда токен бота
CHANNEL_ID = "@https://t.me/uristtanrykazan"  # Вставь юзернейм своего канала
GOOGLE_SHEETS_FILE = "credentials.json"  # Файл с ключами доступа
SPREADSHEET_NAME = "Посты для Telegram"  # Название твоей таблицы в Google Sheets

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

# Подключение к боту
bot = ApplicationBuilder().token(BOT_TOKEN).build()

# Функция публикации постов
def post_to_channel():
    rows = sheet.get_all_records()
    now = datetime.now()

    for i, row in enumerate(rows):
        post_date = datetime.strptime(row['Дата публикации'], '%d.%m.%Y').date()
        post_time = datetime.strptime(row['Время публикации'], '%H:%M').time()
        post_datetime = datetime.combine(post_date, post_time)

        if post_datetime <= now and row['Статус'] == "Не опубликовано":
            bot.send_message(chat_id=CHANNEL_ID, text=row['Текст поста'])
            sheet.update_cell(i + 2, 4, "Опубликовано")  # Обновляет статус

# Планировщик: проверять таблицу каждые 5 минут
schedule.every(5).minutes.do(post_to_channel)

# Запуск бота
while True:
    schedule.run_pending()
    time.sleep(1)