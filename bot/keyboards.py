from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

BACK_BUTTON = InlineKeyboardMarkup()
back_menu = InlineKeyboardButton(text="На главную", callback_data="back_menu")
BACK_BUTTON.add(back_menu)

START_KEYBOARD = InlineKeyboardMarkup()
where_to_go = InlineKeyboardButton(text="🎯 Куда сходить сегодня?", callback_data="start_where")
support = InlineKeyboardButton(text="💬 Обратная связь", callback_data="start_support")
recommend_place = InlineKeyboardButton(text="💡 Предложить заведение", callback_data="start_recommend")
how_to_enter = InlineKeyboardButton(text="Как попасть в бот?", callback_data="start_how-to")
START_KEYBOARD.add(where_to_go).add(support).add(recommend_place).add(how_to_enter)

CHECK_SUBSCRIPTION = InlineKeyboardMarkup()
check_button = InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check")
CHECK_SUBSCRIPTION.add(check_button)

"""CATEGORIES = InlineKeyboardMarkup()
food_button = InlineKeyboardButton(text="🍕 Еда и напитки", callback_data="categ_food")
activities_button = InlineKeyboardButton(text="🎮 Отдых и развлечения", callback_data="categ_activities")
sports_button = InlineKeyboardButton(text="⚽ Спорт и активности", callback_data="categ_sports")
walking_button = InlineKeyboardButton(text="🚶 Где погулять", callback_data="categ_walk")
teenagers_opportunities = InlineKeyboardButton(text="🎓 Возможности для молодёжи", callback_data="categ_teens")
CATEGORIES.add(food_button).add(activities_button).add(sports_button).add(walking_button).add(teenagers_opportunities)"""