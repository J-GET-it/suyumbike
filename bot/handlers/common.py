import random

from functools import wraps
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from bot.texts import START_TEXT, TARGET_CHAT_ID, SUBSCRIBE_TEXT, SUPPORT_TEXT, RECOMMEND_TEXT, ADMIN_ID
from bot.keyboards import START_KEYBOARD, CHECK_SUBSCRIPTION, BACK_BUTTON, back_menu
from bot.models import Category, Place


def start(message: Message):
    """Функция, вызываемая при /start"""
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

    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Выбери категорию", reply_markup = markup)


def support_handler(call: CallbackQuery):
    """Обработчик кнопки Обратная связь"""

    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = SUPPORT_TEXT, reply_markup = BACK_BUTTON)


def recommend_handler(call: CallbackQuery):
    """Обработчик кнопки Предложить заведение"""

    msg = bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = RECOMMEND_TEXT, reply_markup = BACK_BUTTON)
    bot.register_next_step_handler(msg, register_recommend)

def register_recommend(message: Message):
    """Отправка предложения о новом месте"""
    if message.text == "/start":
        start(message)
    bot.send_message(chat_id=message.chat.id, text="Предложение успешно отправлено!")
    bot.send_message(chat_id=ADMIN_ID, text=f"Новое предложение: \n\n{message.text}")

# Обработчик кнопок Категорий и Подкатегорий
def categories_handler(call: CallbackQuery):
    """Обработчик кнопок Категорий и Подкатегорий"""
    try:
        _, pk_, status = call.data.split("_")
        status = int(status)
    except:
        _, pk_ = call.data.split("_")
        status = 0
    category = Category.objects.get(pk=pk_)
    
    if Category.objects.filter(parent_category = category).exists():
        # Получаем подкатегории
        markup = InlineKeyboardMarkup()
        for category_ in Category.objects.filter(parent_category = category):
            markup.add(InlineKeyboardButton(text=category_.name, callback_data=f"category_{category_.pk}"))
        if category.parent_category:
            markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.parent_category.pk}"))
        else:
            markup.add(InlineKeyboardButton(text="Назад", callback_data="start_where"))
        markup.add(back_menu)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Выбери категорию", reply_markup = markup)
    else:
        # Получаем случайное место
        places = Place.objects.filter(category = category)
        try:
            places = places.remove(category)
        except:
            pass
        place = random.choice(places)

        if status == 0:
            if category.description:
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = category.description)
        with open(place.photo.path, 'rb') as photo:
            # Создаем кнопки с ссылками на соц.сети
            markup = InlineKeyboardMarkup()
            if place.vk_link:
                markup.add(InlineKeyboardButton(text="Посмотреть в ВК", url=place.vk_link))
            if place.instagram_link:
                markup.add(InlineKeyboardButton(text="Посмотреть в Instagram", url=place.instagram_link))
            if place.telegram_link:
                markup.add(InlineKeyboardButton(text="Посмотреть в Telegram", url=place.telegram_link))

            # Создаем кнопку с ссылкой на Яндекс.Карты
            markup.add(InlineKeyboardButton(text="Проложить маршрут", url=f"https://yandex.ru/maps/?text={place.name} {place.address}"))

            markup.add(InlineKeyboardButton(text="Следующее место", callback_data=f"category_{category.pk}_1"))
            
            if category.parent_category:
                try:
                    markup.add(InlineKeyboardButton(text="Назад", callback_data=f"start_where"))
                except Exception as e:
                    bot.send_message(chat_id=call.message.chat.id, text=e)

            markup.add(back_menu)
            bot.send_photo(chat_id = call.message.chat.id, photo = photo, caption = place.get_text(), reply_markup = markup)


def back_handler(call: CallbackQuery):
    """Обработчик кнопки назад"""
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    if bot.get_chat_member(chat_id = TARGET_CHAT_ID, user_id = call.message.chat.id).status in ["member", "administrator", "creator"]:
        bot.send_message(chat_id = call.message.chat.id, text = "Главное меню", reply_markup = START_KEYBOARD)
    else:
        bot.send_message(chat_id = call.message.chat.id, text = SUBSCRIBE_TEXT, reply_markup = CHECK_SUBSCRIPTION)