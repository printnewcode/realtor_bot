from functools import wraps
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from bot.models import User, Presentations

def admin_permission(func):
    """
    Checking user for admin permission to access the function.
    """

    @wraps(func)
    def wrapped(message) -> None:
        user_id = message.from_user.id
        user = User.objects.get(user_id=user_id)
        if not user.is_admin:
            bot.send_message(user_id, '⛔ У вас нет администраторского доступа')
            return
        return func(message)

    return wrapped

@admin_permission
def admin_panel(message):
    """Админ-панель"""
    admin = User.objects.get(user_id=message.from_user.id)
    presentations = Presentations.objects.all().order_by('pk')
    reply = InlineKeyboardMarkup()
    for pres in presentations:
        reply.add(InlineKeyboardButton(text=f"Презентация {pres.pk}", callback_data=f"pres_{pres.pk}"))
    try:    
        bot.send_message(text="Вот все презентации!", chat_id=message.chat.id, reply_markup=reply)
    except:
        bot.send_message(text="Презентаций нет!", chat_id=message.chat.id)

def get_pres(call):
    _, data = call.data.split("_")
    presentation = Presentations.objects.get(pk=data)
    bot.send_message(
        text=f"Контактные данные: {presentation.contact}\nID презентации: {presentation.pk}",
        chat_id=call.message.chat.id
    )
    bot.send_document(
        call.message.chat.id, presentation.presentation, caption="Презентация"
    )