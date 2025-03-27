from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


"""User"""
START_BUTTONS = InlineKeyboardMarkup()
start_button = InlineKeyboardButton(text="Предложить площадь в аренду", callback_data="start_presentation")
START_BUTTONS.add(start_button)

TYPE_AREA = ReplyKeyboardMarkup(one_time_keyboard=True)
integrated = KeyboardButton(text="Встроенное")
building = KeyboardButton(text="Здание")
storage = KeyboardButton(text="Склад")
office = KeyboardButton(text="Офис")
TYPE_AREA.add(integrated, building).add(storage, office)

WATER_SUPPLY = ReplyKeyboardMarkup()
water_yes = KeyboardButton(text="Да. Имеется")
water_no = KeyboardButton(text="Нет. Отсутствует")
WATER_SUPPLY.add(water_yes).add(water_no)

TYPE_RENT = ReplyKeyboardMarkup()
type_straight = KeyboardButton(text="Прямая аренда")
type_sub = KeyboardButton(text="Субаренда")
TYPE_RENT.add(type_straight).add(type_sub)

FLOOR_BUTTONS = ReplyKeyboardMarkup()
floor_1 = KeyboardButton(text="1 этаж")
floor_2 = KeyboardButton(text="2 этаж")
floor_3 = KeyboardButton(text="3 этаж")
floor_0 = KeyboardButton(text="Цокольный этаж")
basement = KeyboardButton(text="Подвал")
FLOOR_BUTTONS.add(floor_0).add(floor_1).add(floor_2).add(floor_3).add(basement)

AGGREMENT_BUTTON = ReplyKeyboardMarkup()
agreement = KeyboardButton(text="Даю свое согласие на обработку данных")
AGGREMENT_BUTTON.add(agreement)

SKIP_BUTTON = ReplyKeyboardMarkup()
skip = KeyboardButton(text="Пометки отсутствуют")
SKIP_BUTTON.add(skip)