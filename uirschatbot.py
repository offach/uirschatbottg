import telebot
import requests
import json
from fpdf import FPDF
import io
from PIL import Image, ImageDraw, ImageFont
bot = telebot.TeleBot("token")

admin_id = 233136616 # ID администратора

@bot.message_handler(commands=['help'])
def send_help_message(message):
    bot.forward_message(admin_id, message.chat.id, message.message_id)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     "Здравствуйте! Я бот-инструмент для быстрой проверки контрагентов. В текущий момент подключен к базе данных Damia-zakupki. Введите /inn число - для использования бота. Также можете ознакомиться со всеми возможными командами используя /commands")


@bot.message_handler(commands=['commands'])
def send_help_message(message):
    bot.send_message(message.chat.id,
                     "/start\n/inn - основная команда для получение данных для проверки контрагентов\n/help - команда после которой необходимо написать свой вопрос")


@bot.message_handler(commands=['inn'])
def get_inn_data(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "You did not enter an INN")
    else:
        inns = message.text.split()[1:]
        for inn in inns:
            url = f"https://api.damia.ru/zakupki/zakupki?inn={inn}&fz=44&key=token"
            response = requests.get(url)
            if response.status_code == 200:
                inn_data = json.loads(response.text)
                inn = list(inn_data.keys())[0]
                years = list(inn_data[inn].keys())
                result_text = ""
                for year in years:
                    data = inn_data[inn][year]
                    for status, details in data.items():
                        price = details["Цена"][0]["Сумма"]
                        quantity = details["Цена"][0]["Количество"]
                        currency = details["Цена"][0]["ВалютаНаим"]
                        customers = details["Заказчики"]
                        for customer in customers:
                            ogrn = customer["ОГРН"]
                            inn1 = customer["ИНН"]
                            name = customer["НаимПолн"]
                            address = customer["АдресПолн"]
                            result_text += f"Year: {year}\nStatus: {status}\nPrice: {price} {currency}\nQuantity: {quantity}\nOGRN: {ogrn}\nINN: {inn1}\nName: {name}\nAddress: {address}\n\n"
                        bot.send_message(message.chat.id, result_text)
                        with open("inn_data.txt", "w", encoding="utf-8") as f:
                            f.write(result_text)
                        bot.send_document(message.chat.id, open("inn_data.txt", "rb"))
                        img = Image.new('RGB', (500, 200), color=(73, 109, 137))
                        d = ImageDraw.Draw(img)
                        fnt = ImageFont.truetype('arial.ttf', 16)
                        d.text((10, 10), result_text, font=fnt, fill=(255, 255, 0))
                        img.save('inn_data.png')
                        bot.send_photo(message.chat.id, open('inn_data.png', 'rb'))


bot.polling()