from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


"""User"""
START_BUTTONS = InlineKeyboardMarkup()
start_button = InlineKeyboardButton(text="Создать презентацию", callback_data="start_presentation")
START_BUTTONS.add(start_button)