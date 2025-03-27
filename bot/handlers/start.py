from bot.models import Presentations, User  # Импорт вашей модели в Django
from docx import Document
from docx.shared import Inches
import os
from datetime import datetime
from django.conf import settings

from bot import bot
from bot.handlers.admin import admin_notification
from bot.keyboard import START_BUTTONS, WATER_SUPPLY, AGGREMENT_BUTTON, FLOOR_BUTTONS, TYPE_AREA, TYPE_RENT, \
    SKIP_BUTTON


def start_message(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user = User.objects.update_or_create(
        user_id=message.from_user.id,
        defaults={"user_id": message.from_user.id, "username": message.from_user.username}
    )
    bot.send_message(message.chat.id, "Здравствуйте! Я помогу собрать информацию о помещении",
                     reply_markup=START_BUTTONS,
                     )


def exit_handler(call):
    pres = Presentations.objects.filter(user=User.objects.get(user_id=str(call.message.chat.id))).last()
    pres.delete()
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    start_message(message=call.message)


def ask_question(call):
    pres = Presentations.objects.create(user=User.objects.get(user_id=call.message.chat.id))
    pres.save()

    def check_exit(message) -> bool:
        if message.text == "Прекратить создание предложения":
            pres.delete()
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            return True
        return False

    def create_pres(message):
        if check_exit(message):
            return
        # create_presentation(object=pres)
        bot.send_message(
            text="✉ Информация передана агенту\n\n📞 Наши контакты для связи: +7 933 481 00 01",
            chat_id=message.chat.id,
        )
        admin_notification(pres, message.chat.id)
        return

    def agreement(id_):
        msg = bot.send_message(
            text="Для продолжения нужно подтвердить свое согласие на обработку данных, нажав на кнопку ниже",
            chat_id=id_,
            reply_markup=AGGREMENT_BUTTON,
        )
        bot.register_next_step_handler(msg, create_pres)

    def register_number(message):
        if check_exit(message):
            return
        pres.contact += message.text
        pres.save()
        return agreement(message.chat.id)

    def get_number(id_):
        msg = bot.send_message(
            text="Телефон для связи", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_number)

    def register_contact(message):
        if check_exit(message):
            return
        pres.contact = f"{message.text}\n"
        pres.save()
        return get_number(message.chat.id)

    def get_contact(id_):
        msg = bot.send_message(
            text="Как к вам обращаться (ФИО)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_contact)

    def register_additives(message):
        if check_exit(message):
            return
        if message.text == "Пометки отсутствуют":
            return get_contact(message.chat.id)

        try:
            pres.additives = message.text
        except Exception as e:
            print(e)
        pres.save()
        return get_contact(message.chat.id)

    def get_additives(id_):
        msg = bot.send_message(
            text="Если у вас остались комментарии и пожелания - напишите их сюда\n\nЕсли пометок нет - нажмите на кнопку",
            chat_id=id_, reply_markup=SKIP_BUTTON
        )
        bot.register_next_step_handler(msg, register_additives)

    def register_photo_inside(message):
        if check_exit(message):
            return
        try:
            if message.photo:
                # Получаем информацию о фото (берем последнее, т.к. оно самого высокого качества)
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                # Формируем путь для сохранения
                file_name = f"inside_{message.chat.id}_{message.message_id}.jpg"
                file_path = os.path.join(settings.MEDIA_ROOT, 'temp', file_name)

                # Создаем директории если их нет
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Сохраняем файл
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Сохраняем путь в базу данных
                pres.photo_inside = file_path
                pres.save()
            else:
                bot.reply_to(message, "Пожалуйста, отправьте фотографию")
                return get_photo_inside(message.chat.id)
        except Exception as e:
            print(f"Ошибка при сохранении фото внутри: {e}")
            bot.reply_to(message, "Произошла ошибка при сохранении фото. Попробуйте еще раз.")
            return get_photo_inside(message.chat.id)
        return get_additives(message.chat.id)

    def get_photo_inside(id_):
        msg = bot.send_message(
            text="Отправьте фото внутри помещения (отправьте как фото, не как файл)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_photo_inside)

    def register_photo_outside(message):
        if check_exit(message):
            return
        try:
            if message.photo:
                # Получаем информацию о фото (берем последнее, т.к. оно самого высокого качества)
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                # Формируем путь для сохранения
                file_name = f"outside_{message.chat.id}_{message.message_id}.jpg"
                file_path = os.path.join(settings.MEDIA_ROOT, 'temp', file_name)

                # Создаем директории если их нет
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Сохраняем файл
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Сохраняем путь в базу данных
                pres.photo_outside = file_path
                pres.save()
            else:
                bot.reply_to(message, "Пожалуйста, отправьте фотографию")
                return get_photo_outside(message.chat.id)
        except Exception as e:
            print(f"Ошибка при сохранении фото снаружи: {e}")
            bot.reply_to(message, "Произошла ошибка при сохранении фото. Попробуйте еще раз.")
            return get_photo_outside(message.chat.id)
        return get_photo_inside(message.chat.id)

    def get_photo_outside(id_):
        msg = bot.send_message(
            text="Отправьте фото снаружи помещения (отправьте как фото, не как файл)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_photo_outside)

    def register_plan(message):
        if check_exit(message):
            return
        try:
            if message.photo:
                # Получаем информацию о фото (берем последнее, т.к. оно самого высокого качества)
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                # Формируем путь для сохранения
                file_name = f"plan_{message.chat.id}_{message.message_id}.jpg"
                file_path = os.path.join(settings.MEDIA_ROOT, 'temp', file_name)

                # Создаем директории если их нет
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Сохраняем файл
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Сохраняем путь в базу данных
                pres.plan = file_path
                pres.save()
            else:
                bot.reply_to(message, "Пожалуйста, отправьте фотографию плана")
                return get_plan(message.chat.id)
        except Exception as e:
            print(f"Ошибка при сохранении плана: {e}")
            bot.reply_to(message, "Произошла ошибка при сохранении плана. Попробуйте еще раз.")
            return get_plan(message.chat.id)
        return get_photo_outside(message.chat.id)

    def get_plan(id_):
        msg = bot.send_message(
            text="Отправьте план помещения (отправьте как фото)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_plan)

    def register_type_rent(message):
        if check_exit(message):
            return
        pres.type_rent = message.text
        pres.save()
        return get_plan(message.chat.id)

    def get_type_rent(id_):
        msg = bot.send_message(
            text="Выберите тип аренды помещения", chat_id=id_, reply_markup=TYPE_RENT
        )
        bot.register_next_step_handler(msg, register_type_rent)

    def register_rate(message):
        if check_exit(message):
            return
        pres.rate = message.text
        pres.save()
        return get_type_rent(message.chat.id)

    def get_rate(id_):
        msg = bot.send_message(
            text="Желаемая арендная плата в месяц, рубли/в месяц (указывать только цифры)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_rate)

    def register_height(message):
        if check_exit(message):
            return
        pres.height = message.text
        pres.save()
        return get_rate(message.chat.id)

    def get_height(id_):
        msg = bot.send_message(
            text="Высота потолков помещения, метры (указывать только цифру)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_height)

    def register_floor(message):
        if check_exit(message):
            return
        pres.floor = message.text
        pres.save()
        return get_height(message.chat.id)

    def get_floor(id_):
        msg = bot.send_message(
            text="Выберите на каком этаже ваше помещение", chat_id=id_, reply_markup=FLOOR_BUTTONS
        )
        bot.register_next_step_handler(msg, register_floor)

    def register_water_supply(message):
        if check_exit(message):
            return
        pres.water_supply = message.text
        pres.save()
        return get_floor(message.chat.id)

    def get_water_supply(id_):
        msg = bot.send_message(
            text="Наличие водоснабжения и водоотведения помещения (Да/Нет)", chat_id=id_, reply_markup=WATER_SUPPLY
        )
        bot.register_next_step_handler(msg, register_water_supply)

    def register_power(message):
        if check_exit(message):
            return
        pres.power = message.text
        pres.save()
        return get_water_supply(message.chat.id)

    def get_power(id_):
        msg = bot.send_message(
            text="Мощность, кВт (указывать только цифру)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_power)

    def register_square(message):
        if check_exit(message):
            return
        pres.square = message.text
        pres.save()
        return get_power(message.chat.id)

    def get_square(id_):
        msg = bot.send_message(
            text="Площадь помещения, метры квадратные (указывать только цифру)", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_square)

    def register_adress(message):
        if check_exit(message):
            return
        pres.adress = message.text
        pres.save()
        return get_square(message.chat.id)

    def get_adress(id_):
        msg = bot.send_message(
            text="Адрес помещения", chat_id=id_
        )
        bot.register_next_step_handler(msg, register_adress)

    def register_type_building(message):
        if check_exit(message):
            return

        pres.type_building = message.text
        pres.save()
        return get_adress(message.chat.id)

    def get_type_building(id_):
        msg = bot.send_message(
            text="Выберите тип помещения", chat_id=id_, reply_markup=TYPE_AREA
        )
        bot.register_next_step_handler(msg, register_type_building)

    get_type_building(call.message.chat.id)
    return


def show_all_presentations(call):
    pres = Presentations.objects.all()
    for pre in pres:
        doc = Document()

        doc.add_heading(f"{pre.square} кв.м., {pre.adress}", level=1)
        doc.add_paragraph(f'Здание по адресу: {pre.adress}')
        doc.add_paragraph(f'Площадь: {pre.square}')
        doc.add_paragraph(f'Электроснабжение помещения: {pre.power}')
        doc.add_paragraph(f'Водоснабжение помещения: {pre.water_supply}')
        doc.add_paragraph(f'Высота потолков: {pre.height}')
        doc.add_paragraph(f'Желаемая арендная плата помещения: {pre.rate}')
        doc.add_paragraph(f'Тип аренды помещения: {pre.type_rent}')

        # Добавляем план помещения
        if pre.plan:
            try:
                plan_path = os.path.join(settings.MEDIA_ROOT, str(pre.plan))
                print(f"Путь к плану: {plan_path}")
                print(f"Существует ли файл: {os.path.exists(plan_path)}")
                if os.path.exists(plan_path):
                    doc.add_heading('План помещения', level=2)
                    doc.add_picture(plan_path, width=Inches(6))
                else:
                    print(f"Файл плана не найден по пути: {plan_path}")
            except Exception as e:
                print(f"Ошибка при добавлении плана: {e}")
                print(f"Значение pre.plan: {pre.plan}")
                print(f"Тип pre.plan: {type(pre.plan)}")
        else:
            print("План отсутствует в записи")

        # Добавляем фото снаружи
        if pre.photo_outside:
            try:
                outside_path = os.path.join(settings.MEDIA_ROOT, str(pre.photo_outside))
                if os.path.exists(outside_path):
                    doc.add_heading('Фото снаружи', level=2)
                    doc.add_picture(outside_path, width=Inches(6))
            except Exception as e:
                print(f"Ошибка при добавлении фото снаружи: {e}")

        # Добавляем фото внутри
        if pre.photo_inside:
            try:
                inside_path = os.path.join(settings.MEDIA_ROOT, str(pre.photo_inside))
                if os.path.exists(inside_path):
                    doc.add_heading('Фото внутри', level=2)
                    doc.add_picture(inside_path, width=Inches(6))
            except Exception as e:
                print(f"Ошибка при добавлении фото внутри: {e}")

        # Добавляем примечания
        if pre.additives and pre.additives != "0":
            doc.add_heading('Дополнительные примечания', level=2)
            doc.add_paragraph(pre.additives)

        # Сохраняем документ с уникальным именем
        doc_name = f'presentation_{pre.user.user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
        doc_path = os.path.join(settings.MEDIA_ROOT, 'temp', doc_name)

        # Создаем директорию для временных файлов, если её нет
        os.makedirs(os.path.dirname(doc_path), exist_ok=True)

        doc.save(doc_path)

        # Отправляем документ пользователю
        try:
            with open(doc_path, 'rb') as doc_file:
                pre.presentation = doc_path
                pre.save()
                bot.send_document(call.message.chat.id, doc_file, caption="Вот ваша презентация!")

        except Exception as e:
            print(f"Ошибка при отправке документа: {e}")
        finally:
            # Удаляем файл после отправки
            try:
                os.remove(doc_path)
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")


@bot.message_handler(commands=['presentations'])
def handle_presentations(message):
    """Обработчик команды /presentations"""
    try:
        user = User.objects.filter(user_id=message.chat.id).first()
    except:
        print("Пользователь незарегистрирован")
    try:
        pres = Presentations.objects.filter(user=user)
        if not pres.exists():
            bot.reply_to(message, "Пока нет ни одной презентации.")
            return

        for pre in pres:
            doc = Document()

            doc.add_heading(f'{pre.square} кв.м., {pre.adress}', level=1)
            doc.add_paragraph(f'Ставка аренды: {pre.rate} руб.')
            doc.add_paragraph(f'Площадь: {pre.square} кв.м.')
            if pre.photo_outside:
                try:
                    outside_path = os.path.join(settings.MEDIA_ROOT, str(pre.photo_outside))
                    if os.path.exists(outside_path):
                        doc.add_heading('Фото снаружи', level=2)
                        doc.add_picture(outside_path, width=Inches(6))
                except Exception as e:
                    print(f"Ошибка при добавлении фото снаружи: {e}")
            doc.add_heading("Характеристики")
            doc.add_paragraph(f'Тип помещения: {pre.type_building}')
            doc.add_paragraph(f'Расположение по адресу: {pre.adress}')
            doc.add_paragraph(f'Площадь помещения: {pre.square} кв.м.')
            doc.add_paragraph(f'Мощность: {pre.power} кВт')
            doc.add_paragraph(f'Водоснабжение помещения: {pre.water_supply}')
            doc.add_paragraph(f'Высота потолков: {pre.height} метра')
            doc.add_paragraph(f'Тип аренды помещения: {pre.type_rent}')
            # Добавляем план помещения
            if pre.plan:
                try:
                    plan_path = os.path.join(settings.MEDIA_ROOT, str(pre.plan))
                    print(f"Путь к плану: {plan_path}")
                    print(f"Существует ли файл: {os.path.exists(plan_path)}")
                    if os.path.exists(plan_path):
                        doc.add_heading('План помещения', level=2)
                        doc.add_picture(plan_path, width=Inches(6))
                    else:
                        print(f"Файл плана не найден по пути: {plan_path}")
                except Exception as e:
                    print(f"Ошибка при добавлении плана: {e}")
                    print(f"Значение pre.plan: {pre.plan}")
                    print(f"Тип pre.plan: {type(pre.plan)}")
            else:
                print("План отсутствует в записи")

                # Добавляем фото внутри
            if pre.photo_inside:
                try:
                    inside_path = os.path.join(settings.MEDIA_ROOT, str(pre.photo_inside))
                    if os.path.exists(inside_path):
                        doc.add_heading('Фото внутри', level=2)
                        doc.add_picture(inside_path, width=Inches(6))
                except Exception as e:
                    print(f"Ошибка при добавлении фото внутри: {e}")

            # Добавляем примечания
            if pre.additives and pre.additives != "0":
                doc.add_heading('Дополнительные примечания', level=2)
                doc.add_paragraph(pre.additives)

            # Сохраняем документ с уникальным именем
            doc_name = f'presentation_{pre.user.user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
            doc_path = os.path.join(settings.MEDIA_ROOT, 'temp', doc_name)

            # Создаем директорию для временных файлов, если её нет
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)

            doc.save(doc_path)

            # Отправляем документ пользователю
            try:
                with open(doc_path, 'rb') as doc_file:
                    bot.send_document(message.chat.id, doc_file,
                                      caption=f"Презентация для помещения по адресу: {pre.adress}")
            except Exception as e:
                print(f"Ошибка при отправке документа: {e}")
                bot.reply_to(message, "Произошла ошибка при отправке документа.")
            finally:
                # Удаляем файл после отправки
                try:
                    os.remove(doc_path)
                except Exception as e:
                    print(f"Ошибка при удалении файла: {e}")

    except Exception as e:
        print(f"Общая ошибка: {e}")
        bot.reply_to(message, f"Произошла ошибка при создании презентаций: {str(e)}")
