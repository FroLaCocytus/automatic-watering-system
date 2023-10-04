from telebot import types

# Главная клавиатура
def main_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton("Растение 🌳", callback_data='title_button1'))
    keyboard.row(types.InlineKeyboardButton("Полить", callback_data='plant_button1'),
            types.InlineKeyboardButton("Информация", callback_data='plant_button2'),
            types.InlineKeyboardButton("Добавить", callback_data='plant_button3'))
    keyboard.row(types.InlineKeyboardButton("Ёмкость 💧", callback_data='title_button2'))
    keyboard.row(types.InlineKeyboardButton("Информация", callback_data='container_button1'))

    return keyboard
    

# Клавиатура выбора (да/нет)
def condition_keyboard(yes, no):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(types.InlineKeyboardButton("Да", callback_data=yes),
               types.InlineKeyboardButton("Нет", callback_data=no))

    return keyboard

# Создание клавиатуры из массива
def create_inline_keyboard(array_value, key_word):
    keyboard = types.InlineKeyboardMarkup()
    for value in array_value:
        button = types.InlineKeyboardButton(text=value[1], callback_data=f'{key_word}_{value[1]}_{value[0]}')
        keyboard.row(button)
    
    return keyboard
    
