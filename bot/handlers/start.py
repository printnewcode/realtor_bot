import os

import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.core.files import File
from django.core.files.base import ContentFile
from bot.models import Presentations, User  # Импорт вашей модели в Django
from io import BytesIO
from fpdf import FPDF
import nelsie
import requests

from bot import bot
from bot.static.qna import QUESTIONS
from Realtor.settings import OWNER_ID, BOT_TOKEN
from bot.keyboard import START_BUTTONS

# Хранение данных пользователя
"""adress=""
square=""
power=""
water_supply=""
height=""
rate=""
type_rent=""
plan=""
photo_inside=""
photo_outside=""
additives=""
"""
def download_image(file_id):
    # Здесь укажите ваш токен бота
    file_info = bot.get_file(file_id)
    downloaded_file=bot.download_file(file_info.file_path)

    src = "bot/handlers/files/"+file_info.file_path
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    img = open(src, 'rb')
    return img
# Функция для создания PDF-презентации

def create_pdf_presentation(object):
    # Создаем экземпляр PDF
    answers = [object.adress, object.square,object.power,object.water_supply,object.height,object.rate,object.type_rent,object.plan,object.photo_inside,object.photo_outside,object.additives]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    photo_plan = download_image(file_id=object.plan)
    photo_inside=download_image(file_id=object.photo_inside)
    photo_outside=download_image(file_id=object.photo_outside)

    # Первый слайд: Информация о расположении, водопроводе, электричестве
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Информация о помещении', ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f'Расположение: {object.adress}')
    pdf.multi_cell(0, 10, f'Водопровод: {object.water_supply}')
    pdf.multi_cell(0, 10, f'Электричество: {object.power}')

    # Второй слайд: Информация о цене и типе аренды
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Цена и тип аренды', ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f'Предпочитаемая цена: {object.rate}')
    pdf.multi_cell(0, 10, f'Тип аренды: {object.type_rent}')

    # Третий слайд: Фото изнутри и адрес
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Фото и адрес', ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f'Адрес: {object.adress}')
    
    # Загружаем и вставляем изображение по file_id2
    image_file = photo_plan
    if image_file:
        pdf.image(image_file, x=10, w=190)

    # Четвертый слайд: Фото внутри, высота потолков и площадь
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Дополнительные параметры', ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f'Высота потолков: {object.height}')
    pdf.multi_cell(0, 10, f'Площадь: {object.square}')
    
    # Загружаем и вставляем изображение по file_id3
    image_file = photo_inside
    if image_file:
        pdf.image(image_file, x=10, w=190)

    # Пятый слайд: Дополнительная информация
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Дополнительная информация', ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, object.additives)

    # Сохранение PDF файла
    pdf_file_name = 'presentation.pdf'
    pdf.output(pdf_file_name)
    return pdf_file_name

def start_message(message):
    user = User.objects.update_or_create(
        user_id=message.from_user.id,
        defaults={"user_id": message.from_user.id, "username": message.from_user.username}
    )
    create_pdf_presentation(object=Presentations.objects.filter(user=User.objects.get(user_id=message.from_user.id)).last())
    bot.send_message(message.chat.id, "Здравствуйте! Я помогу собрать информацию о помещении.",
                     reply_markup=START_BUTTONS)


"""def create_presentation(object):
# Функция для загрузки изображения из Telegram по file_id"""




"""print(object.adress, object.height)
    slides = nelsie.SlideDeck()
    for x in range(5):
        slide = slides.new_slide(bg_color="white")
        slide.text(object.adress)
    slides.render("slides.pdf")
    object.presentation = slides.render("slides.pdf")
    object.save()"""


def ask_question(call):
    pres = Presentations.objects.create(user=User.objects.get(user_id=call.message.chat.id))
    pres.save()

    def create_pres():
        a = create_pdf_presentation(object=pres)
        bot.send_message(
            text=a,
            chat_id=call.message.chat.id
        )

    def register_additives(message):
        try:
            pres.additives = message.text
        except Exception as e:
            print(e)
        pres.save()
        return create_pres()

    def get_additives(id_):
        msg = bot.send_message(
            text="Отправьте доп.пометки", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_additives)

    def register_photo_inside(message):
        try:
            pres.photo_inside = message.photo[len(message.photo)-1].file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_additives(message.chat.id)

    def get_photo_inside(id_):
        msg = bot.send_message(
            text="Отправьте фото внутри помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_photo_inside)

    def register_photo_outside(message):
        try:
            pres.photo_outside = message.photo[len(message.photo)-1].file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_photo_inside(message.chat.id)

    def get_photo_outside(id_):
        msg = bot.send_message(
            text="Отправьте фото снаружи помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_photo_outside)

    def register_plan(message):
        try:
            pres.plan = message.photo[len(message.photo)-1].file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_photo_outside(message.chat.id)

    def get_plan(id_):
        msg = bot.send_message(
            text="Отправьте план помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_plan)

    def register_type_rent(message):
        pres.type_rent = message.text
        pres.save()
        return get_plan(message.chat.id)

    def get_type_rent(id_):
        msg = bot.send_message(
            text="Отправьте тип аренды помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_type_rent)

    def register_rate(message):
        pres.rate = message.text
        pres.save()
        return get_type_rent(message.chat.id)

    def get_rate(id_):
        msg = bot.send_message(
            text="Отправьте желаемую арендную плату помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_rate)

    def register_height(message):
        pres.height = message.text
        pres.save()
        return get_rate(message.chat.id)

    def get_height(id_):
        msg = bot.send_message(
            text="Отправьте высоту потолков помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_height)

    def register_water_supply(message):
        pres.water_supply = message.text
        pres.save()
        return get_height(message.chat.id)

    def get_water_supply(id_):
        msg = bot.send_message(
            text="Отправьте водоснабжение помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_water_supply)

    def register_power(message):
        pres.power = message.text
        pres.save()
        return get_water_supply(message.chat.id)

    def get_power(id_):
        msg = bot.send_message(
            text="Отправьте электроснабжение помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_power)

    def register_square(message):
        pres.square = message.text
        pres.save()
        return get_power(message.chat.id)

    def get_square(id_):
        msg = bot.send_message(
            text="Отправьте площадь помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_square)

    def register_adress(message):
        pres.adress = message.text
        pres.save()
        return get_square(message.chat.id)

    def get_adress(id_):
        msg = bot.send_message(
            text="Отправьте адрес помещения", chat_id=id_,
        )
        bot.register_next_step_handler(msg, register_adress)

    get_adress(call.message.chat.id)


"""@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if chat_id in user_data and user_data[chat_id][-1] is None:
        user_data[chat_id][-1] = message.text
        next_question_index = len(user_data[chat_id])
        ask_question(chat_id, next_question_index)
    
    elif message.content_type == 'photo':
        user_data[chat_id][-1] = message.photo[-1].file_id
        next_question_index = len(user_data[chat_id])
        ask_question(chat_id, next_question_index)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data[chat_id][-1] = message.document.file_id
        next_question_index = len(user_data[chat_id])
        ask_question(chat_id, next_question_index)

def create_presentation(chat_id):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # пустой слайд

    # Добавление информации в слайд
    for question, answer in zip(questions, user_data[chat_id]):
        textbox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(5))
        text_frame = textbox.text_frame
        text_frame.text = f"{question} {answer}"

    presentation_path = 'presentation.pptx'
    prs.save(presentation_path)

    # Отправляем пользователю
    with open(presentation_path, 'rb') as f:
        bot.send_document(chat_id, f)

    # Очищаем данные пользователя
    del user_data[chat_id]

"""
