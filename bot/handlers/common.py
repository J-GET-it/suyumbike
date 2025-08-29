import random

from functools import wraps
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from bot import bot
from bot.texts import START_TEXT, TARGET_CHAT_ID, SUBSCRIBE_TEXT, SUPPORT_TEXT, HOW_TO_TEXT
from bot.keyboards import START_KEYBOARD, CHECK_SUBSCRIPTION, BACK_BUTTON, back_menu
from bot.models import Category, Place
from bot.models import User
from datetime import date
from django.db import models


def start(message: Message):
    """Функция, вызываемая при /start"""
    # Создаем пользователя, если его еще нет
    User.objects.get_or_create(telegram_id=str(message.chat.id))
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(chat_id = message.chat.id, text = START_TEXT)
    
    # Проверяем подписку человека на группу
    if bot.get_chat_member(chat_id = TARGET_CHAT_ID, user_id = message.chat.id).status in ["member", "administrator", "creator"]:
        bot.send_message(chat_id = message.chat.id, text = "Главное меню", reply_markup = START_KEYBOARD)
    else:
        bot.send_message(chat_id = message.chat.id, text = SUBSCRIBE_TEXT, reply_markup = CHECK_SUBSCRIPTION)


# Обработчики кнопок из меню
def where_to_go_handler(call: CallbackQuery):
    """Обработчик кнопки Куда пойти?"""

    # Получаем категории
    markup = InlineKeyboardMarkup()
    for category in Category.objects.filter(parent_category__isnull=True):
        markup.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.pk}"))
    markup.add(back_menu)
    try:
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Выбери категорию", reply_markup = markup)
    except:
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass
        bot.send_message(chat_id = call.message.chat.id, text = "Выбери категорию", reply_markup = markup)


def support_handler(call: CallbackQuery):
    """Обработчик кнопки Обратная связь"""

    try:
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = SUPPORT_TEXT, reply_markup = BACK_BUTTON)
    except:
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass
        bot.send_message(chat_id = call.message.chat.id, text = SUPPORT_TEXT, reply_markup = BACK_BUTTON)


def how_to_handler(call: CallbackQuery):
    """Обработчик кнопки Предложить заведение"""

    try:
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = HOW_TO_TEXT, reply_markup = BACK_BUTTON)
    except:
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass
        bot.send_message(chat_id = call.message.chat.id, text = HOW_TO_TEXT, reply_markup = BACK_BUTTON)

# Обработчик кнопок Категорий и Подкатегорий
def categories_handler(call: CallbackQuery):
    """Обработчик кнопок Категорий и Подкатегорий"""
    try:
        parts = call.data.split("_")
        if len(parts) == 5:
            _, pk_, status, place_pk, shown_pks = parts
            status = int(status)
            place_pk = int(place_pk)
            shown_pks = list(map(int, shown_pks.split(",")) if shown_pks else [])
        elif len(parts) == 4:
            _, pk_, status, place_pk = parts
            status = int(status)
            place_pk = int(place_pk)
            shown_pks = [place_pk] if place_pk != -1 else []
        elif len(parts) == 3:
            _, pk_, _ = parts
            status = 0
            place_pk = -1
            shown_pks = []
        else:
            _, pk_ = parts
            status = 0
            place_pk = -1
            shown_pks = []
    except Exception as e:
        _, pk_ = call.data.split("_")
        status = 0
        place_pk = -1
        shown_pks = []
    category = Category.objects.get(pk=pk_)
    
    # Добавляем нажатие в статистику по категории, если нажатие было из списка категорий
    if status == 0 and len(call.data.split("_")) != 3:
        category.day_clicks += 1
        category.week_clicks += 1
        category.month_clicks += 1
        category.all_clicks += 1
        category.save()

    if Category.objects.filter(parent_category = category).exists():
        markup = InlineKeyboardMarkup()
        for category_ in Category.objects.filter(parent_category = category).order_by('order'):
            markup.add(InlineKeyboardButton(text=category_.name, callback_data=f"category_{category_.pk}"))
        if category.parent_category:
            markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.parent_category.pk}_2"))
        else:
            markup.add(InlineKeyboardButton(text="Назад", callback_data="start_where"))
        markup.add(back_menu)
        try:
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Выбери категорию", reply_markup = markup)
        except:
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            except:
                pass
            bot.send_message(chat_id = call.message.chat.id, text = "Выбери категорию", reply_markup = markup)
    else:
        # Получаем все места в категории
        all_places = Place.objects.filter(category=category).filter(
            models.Q(date_until__isnull=True) | models.Q(date_until__gte=date.today())
        )
        # Если мест нет вообще (первый показ)
        if not all_places.exists():
            markup = InlineKeyboardMarkup()
            if category.parent_category:
                markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.parent_category.pk}_2"))
            else:
                markup.add(InlineKeyboardButton(text="Назад", callback_data="start_where"))
            markup.add(back_menu)
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Нет доступных мест в этой категории.", reply_markup=markup)
            except Exception:
                bot.send_message(chat_id=call.message.chat.id, text="Нет доступных мест в этой категории.", reply_markup=markup)
            return
        # Исключаем уже показанные
        places = all_places.exclude(pk__in=shown_pks) if shown_pks else all_places
        # Если все места уже были показаны, сбрасываем shown_pks и показываем заново, но исключаем последнее показанное место
        if not places.exists():
            shown_pks = []
            places = all_places.exclude(pk=place_pk) if place_pk != -1 else all_places
        place = random.choice(list(places))
        shown_pks.append(place.pk)
        
        markup = InlineKeyboardMarkup()
        if place.web_link:
            markup.add(InlineKeyboardButton(text="Перейти на сайт", url=place.web_link))
        if place.vk_link:
            markup.add(InlineKeyboardButton(text="Посмотреть в ВК", url=place.vk_link))
        if place.instagram_link:
            markup.add(InlineKeyboardButton(text="Посмотреть в Instagram", url=place.instagram_link))
        if place.telegram_link:
            markup.add(InlineKeyboardButton(text="Посмотреть в Telegram", url=place.telegram_link))
        if place.map_link:
            markup.add(InlineKeyboardButton(text="Проложить маршрут", url=f"{place.map_link}"))
        markup.add(InlineKeyboardButton(
            text="Следующее место",
            callback_data=f"category_{category.pk}_1_{place.pk}_{','.join(map(str, shown_pks))}"
        ))

        if category.parent_category:
            markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.parent_category.pk}_2"))
        else:
            markup.add(InlineKeyboardButton(text="Назад", callback_data="start_where"))
        markup.add(back_menu)

        place_text = place.get_text()
        if status == 0 and category.description:
            place_text = f"{category.description}\n\n{place_text}"

        try:
            # status=0: первое место, call.message - текстовое.
            # status=1: следующее место, call.message - от предыдущего места (может быть с фото).
            if status == 0:
                if place.photo:
                    # Нельзя отредактировать текстовое сообщение в сообщение с фото.
                    try:
                        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    except:
                        pass
                    with open(place.photo.path, 'rb') as photo:
                        bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=place_text, reply_markup=markup)
                else:
                    bot.edit_message_text(text=place_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            elif status == 1:
                has_prev_photo = call.message.photo is not None
                if place.photo:
                    with open(place.photo.path, 'rb') as photo_file:
                        if has_prev_photo:
                             media = InputMediaPhoto(media=photo_file.read(), caption=place_text)
                             bot.edit_message_media(media=media, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
                        else:
                            # prev text, new photo -> delete and send
                            try:
                                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                            except:
                                pass
                            bot.send_photo(chat_id=call.message.chat.id, photo=photo_file, caption=place_text, reply_markup=markup)
                else: # no new photo
                    if has_prev_photo:
                        # prev photo, new text -> delete and send
                        try:
                            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                        except:
                            pass
                        bot.send_message(chat_id=call.message.chat.id, text=place_text, reply_markup=markup)
                    else:
                        # prev text, new text -> edit
                        bot.edit_message_text(text=place_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            bot.send_message(chat_id=call.message.chat.id, text=f"Произошла ошибка: {e}")


# Обработчики служебных кнопок
def back_handler(call: CallbackQuery):
    """Обработчик кнопки назад"""
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    if bot.get_chat_member(chat_id = TARGET_CHAT_ID, user_id = call.message.chat.id).status in ["member", "administrator", "creator"]:
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Главное меню", reply_markup=START_KEYBOARD)
        except:
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            except:
                pass
            bot.send_message(chat_id=call.message.chat.id, text="Главное меню", reply_markup=START_KEYBOARD)
    else:
        bot.send_message(chat_id = call.message.chat.id, text = SUBSCRIBE_TEXT, reply_markup = CHECK_SUBSCRIPTION)


def check_handler(call: CallbackQuery):
    """Обработчик кнопки Проверить подписку"""
    if bot.get_chat_member(chat_id = TARGET_CHAT_ID, user_id = call.message.chat.id).status in ["member", "administrator", "creator"]:
        bot.send_message(chat_id = call.message.chat.id, text = "Главное меню", reply_markup = START_KEYBOARD)
    else:
        bot.send_message(chat_id = call.message.chat.id, text = SUBSCRIBE_TEXT, reply_markup = CHECK_SUBSCRIPTION)

