import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from pptx import Presentation
from pptx.util import Inches
from django.core.files import File
from django.core.files.base import ContentFile
from bot.models import Presentations, User  # Импорт вашей модели в Django
from io import BytesIO
import pdfkit  # Для конвертации PPTX в PDF

from bot import bot
from bot.static.qna import QUESTIONS
from Realtor.settings import OWNER_ID
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
def start_message(message):
    user = User.objects.update_or_create(
        user_id = message.from_user.id,
        defaults={"user_id":message.from_user.id,"username":message.from_user.username}
    )
    bot.send_message(message.chat.id, "Здравствуйте! Я помогу собрать информацию о помещении.", reply_markup=START_BUTTONS)
    

def ask_question(call):
    pres = Presentations.objects.create(user=User.objects.get(user_id=call.message.chat.id))
    pres.save()
    get_adress(call.message.chat.id)
    def get_adress(id):
        msg=bot.send_message(
            text="Отправьте адрес помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_adress)
    def register_adress(message):
        pres.adress=message.text
        pres.save()
        return get_square(message.chat.id)
    def get_square(id):
        msg=bot.send_message(
            text="Отправьте площадь помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_square)
    def register_square(message):
        pres.square=message.text
        pres.save()
        return get_power(message.chat.id)
    def get_power(id):
        msg=bot.send_message(
            text="Отправьте электроснабжение помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_power)
    def register_power(message):
        pres.power=message.text
        pres.save()
        return get_water_supply(message.chat.id)
    def get_water_supply(id):
        msg=bot.send_message(
            text="Отправьте водоснабжение помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_water_supply)
    def register_water_supply(message):
        pres.water_supply=message.text
        pres.save()
        return get_height(message.chat.id)
    def get_height(id):
        msg=bot.send_message(
            text="Отправьте высоту потолков помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_height)
    def register_height(message):
        pres.power=message.text
        pres.save()
        return get_rate(message.chat.id)
    def get_rate(id):
        msg=bot.send_message(
            text="Отправьте желаемую арендную плату помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_rate)
    def register_rate(message):
        pres.rate=message.text
        pres.save()
        return get_type_rent(message.chat.id)
    def get_type_rent(id):
        msg=bot.send_message(
            text="Отправьте тип аренды помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_type_rent)
    def register_type_rent(message):
        pres.type_rent=message.text
        pres.save()
        return get_plan(message.chat.id)
    def get_plan(id):
        msg=bot.send_message(
            text="Отправьте план помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_plan)
    def register_plan(message):
        try:
            pres.plan=message.document.file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_photo_outside(message.chat.id)
    def get_photo_outside(id):
        msg=bot.send_message(
            text="Отправьте фото снаружи помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_photo_outside)
    def register_photo_outside(message):
        try:
            pres.photo_outside=message.document.file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_photo_inside(message.chat.id)
    def get_photo_inside(id):
        msg=bot.send_message(
            text="Отправьте фото внутри помещения",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_photo_inside)
    def register_photo_inside(message):
        try:
            pres.photo_inside=message.document.file_id
        except Exception as e:
            print(e)
        pres.save()
        return get_additives(message.chat.id)
    def get_additives(id):
        msg=bot.send_message(
            text="Отправьте доп.пометки",
            chat_id=id,
        )
        bot.register_next_step_handler(msg, register_additives)
    def register_additives(message):
        try:
            pres.additives=message.text
        except Exception as e:
            print(e)
        pres.save()
        return
    pres.save()
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