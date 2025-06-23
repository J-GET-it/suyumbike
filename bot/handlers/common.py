import random

from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from bot.texts import START_TEXT, TARGET_CHAT_ID, SUBSCRIBE_TEXT, SUPPORT_TEXT, RECOMMEND_TEXT
from bot.keyboards import START_KEYBOARD, CHECK_SUBSCRIPTION, BACK_BUTTON, back_menu
from bot.models import Category, Place


def start(message: Message):
    """Функция, вызываемая при /start"""

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
    for category in Category.objects.filter(category__isnull=True):
        markup.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.pk}"))
    markup.add(back_menu)

    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Выбери категорию", reply_markup = markup)


def support_handler(call: CallbackQuery):
    """Обработчик кнопки Обратная связь"""

    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = SUPPORT_TEXT, reply_markup = BACK_BUTTON)


def recommend_handler(call: CallbackQuery):
    """Обработчик кнопки Предложить заведение"""

     bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = RECOMMEND_TEXT, reply_markup = BACK_BUTTON)


# Обработчик кнопок Категорий и Подкатегорий
def categories_handler(call: CallbackQuery):
    """Обработчик кнопок Категорий и Подкатегорий"""

    _, pk_ = call.data.split("_")
    category = Category.objects.get(pk=pk_)
    
    if category.has_children:
        # Получаем подкатегории
        markup = InlineKeyboardMarkup()
        for category_ in Category.objects.filter(category = category):
            markup.add(InlineKeyboardButton(text=category_.name, callback_data=f"category_{category_.pk}"))
        if category.category:
            markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.category.pk}"))
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

            markup.add(InlineKeyboardButton(text="Следующее место", callback_data=f"category_{category.pk}"))
            
            if category.category:
                markup.add(InlineKeyboardButton(text="Назад", callback_data=f"category_{category.category.pk}"))
        
            markup.add(back_menu)
            bot.send_photo(chat_id = call.message.chat.id, photo = photo, caption = place.get_text, reply_markup = markup)