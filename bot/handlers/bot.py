import os
import telebot
from telebot import types
from telebot.handler_backends import StatesGroup, State
from telebot.storage import StateMemoryStorage
from django.conf import settings
from fpdf import FPDF
from bot.models import Presentations

state_storage = StateMemoryStorage()
bot = telebot.TeleBot("YOUR_BOT_TOKEN", state_storage=state_storage)


class MyStates(StatesGroup):
    location = State()
    area = State()
    photo = State()


def generate_pdf(room):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Локация: {room.location}", ln=1, align='L')
    pdf.cell(200, 10, txt=f"Площадь: {room.area} кв.м", ln=2, align='L')

    photo_path = os.path.join(settings.MEDIA_ROOT, room.photo.name)
    if os.path.exists(photo_path):
        pdf.image(photo_path, x=10, y=40, w=100)

    pdf_output_path = os.path.join(settings.MEDIA_ROOT, 'room_pdfs', f'room_{room.id}.pdf')
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    pdf.output(pdf_output_path)

    room.pdf_file.name = os.path.join('room_pdfs', f'room_{room.id}.pdf')
    room.save()


def start(message):
    bot.send_message(message.chat.id, "Введите локацию помещения:")
    bot.set_state(message.from_user.id, MyStates.location, message.chat.id)


@bot.message_handler(state=MyStates.location)
def get_location(message):
    bot.send_message(message.chat.id, "Теперь введите площадь помещения (кв.м):")
    bot.add_data(message.from_user.id, message.chat.id, location=message.text)
    bot.set_state(message.from_user.id, MyStates.area, message.chat.id)


@bot.message_handler(state=MyStates.area)
def get_area(message):
    try:
        area = float(message.text)
        bot.send_message(message.chat.id, "Отправьте фото помещения:")
        bot.add_data(message.from_user.id, message.chat.id, area=area)
        bot.set_state(message.from_user.id, MyStates.photo, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")


@bot.message_handler(state=MyStates.photo, content_types=['photo'])
def get_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        photo_path = os.path.join(settings.MEDIA_ROOT, 'room_photos', f'{file_info.file_id}.jpg')
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        with open(photo_path, 'wb') as f:
            f.write(downloaded_file)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            location = data['location']
            area = data['area']

        room = Room.objects.create(
            location=location,
            area=area,
            photo=f'room_photos/{file_info.file_id}.jpg',
            pdf_file=''
        )

        generate_pdf(room)

        with open(os.path.join(settings.MEDIA_ROOT, room.pdf_file.name), 'rb') as pdf:
            bot.send_document(message.chat.id, pdf)

        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")