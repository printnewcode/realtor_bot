from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


"""User"""
EXIT_BUTTON = InlineKeyboardMarkup()
exit = InlineKeyboardButton(text="Прекратить создание предложения", callback_data="exit_")
EXIT_BUTTON.add(exit)
EXIT_REPLY = ReplyKeyboardMarkup(one_time_keyboard=True)
exit_reply = KeyboardButton("Прекратить создание предложения")
EXIT_REPLY.add(exit_reply)

START_BUTTONS = InlineKeyboardMarkup()
start_button = InlineKeyboardButton(text="Предложить площадь в аренду", callback_data="start_presentation")
START_BUTTONS.add(start_button)

TYPE_AREA = ReplyKeyboardMarkup(one_time_keyboard=True)
integrated = KeyboardButton(text="Встроенное")
building = KeyboardButton(text="Здание")
storage = KeyboardButton(text="Склад")
office = KeyboardButton(text="Офис")
TYPE_AREA.add(integrated, building).add(storage, office).add(exit_reply)

WATER_SUPPLY = ReplyKeyboardMarkup(one_time_keyboard=True)
water_yes = KeyboardButton(text="Да. Имеется")
water_no = KeyboardButton(text="Нет. Отсутствует")
WATER_SUPPLY.add(water_yes).add(water_no).add(exit_reply)

TYPE_RENT = ReplyKeyboardMarkup(one_time_keyboard=True)
type_straight = KeyboardButton(text="Прямая аренда")
type_sub = KeyboardButton(text="Субаренда")
TYPE_RENT.add(type_straight).add(type_sub).add(exit_reply)

FLOOR_BUTTONS = ReplyKeyboardMarkup(one_time_keyboard=True)
floor_1 = KeyboardButton(text="1 этаж")
floor_2 = KeyboardButton(text="2 этаж")
floor_3 = KeyboardButton(text="3 этаж")
floor_0 = KeyboardButton(text="Цокольный этаж")
basement = KeyboardButton(text="Подвал")
FLOOR_BUTTONS.add(floor_0).add(floor_1).add(floor_2).add(floor_3).add(basement).add(exit_reply)

AGGREMENT_BUTTON = ReplyKeyboardMarkup(one_time_keyboard=True)
agreement = KeyboardButton(text="Даю свое согласие на обработку данных")
AGGREMENT_BUTTON.add(agreement).add(exit_reply)

SKIP_BUTTON = ReplyKeyboardMarkup(one_time_keyboard=True)
skip = KeyboardButton(text="Пометки отсутствуют")
SKIP_BUTTON.add(skip).add(exit_reply)