import telebot
from telebot import types
import requests

#Вспомогательные функции
from user import get_fullname
from plant import PlantHandler
from keyboards import main_keyboard
import SQL_request as PSQL


# Константы
bot_token = '6669141366:AAFoCkZde_5qfsBYAlTksPkQoQII4w6NIZM'
bot = telebot.TeleBot(bot_token)

# Временное хранилищи информации
user_data = {}



################################### КОМАНДЫ ###################################

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    PSQL.add_user(message.from_user.username)
    answer = f"Привет, {get_fullname(message)}, я чат-бот автополива растений!\n\n" \
              f"Вот мои комманды:\n" \
              f"/menu – вывести основное меню"
    bot.send_message(message.chat.id, answer)

# Обработчик команды /menu
@bot.message_handler(commands=['menu'])
def handle_start(message):
    bot.send_message(message.chat.id, f'Выберите действие которое вы хотите выполнить', reply_markup=main_keyboard())



################################### КНОПКИ ###################################

# Обработчик кнопок-заголовков
@bot.callback_query_handler(func=lambda call: call.data in ['title_button1', 'title_button2', 'container_button1'])
def handle_title_button(call):
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)

# Обработчик инлайн-кнопок связанных с растением
@bot.callback_query_handler(func=lambda call: call.data in ['plant_button1', 'plant_button2', 'plant_button3'])
def handle_plant_button(call):
    # Кнопка полива
    if call.data == 'plant_button1':
        plants_buttons = PSQL.get_plants_buttons(call.from_user.username, 'water')
        if plants_buttons: 
            bot.send_message(call.message.chat.id, 'Выберите растение для полива', reply_markup=plants_buttons)
        else:
            bot.send_message(call.message.chat.id, 'У вас нету растений')
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    # Кнопка просмотра информации
    elif call.data == 'plant_button2':
        plants_buttons = PSQL.get_plants_buttons(call.from_user.username, 'info')
        if plants_buttons: 
            bot.send_message(call.message.chat.id, 'Выберите растение для просмотра информации', reply_markup=plants_buttons)
        else:
            bot.send_message(call.message.chat.id, 'У вас нету растений')
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    # Кнопка добавления
    elif call.data == 'plant_button3':
        chat_id = call.message.chat.id
        user_data[chat_id] = {}
        user_data[chat_id]['plant'] = PlantHandler(bot)
        user_data[chat_id]['plant'].add_plant(call)
        

# Обертка для обработчика варианта "да" и "нет" при добавлении растения 
@bot.callback_query_handler(func=lambda call: call.data in ['add_yes', 'add_no'])
def handle_add_confirmation_wrapper(call):

    chat_id = call.message.chat.id
    if not chat_id in user_data:
            return
    user_data[chat_id]['plant'].add_confirmation(call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    del user_data[chat_id]

# Обработчик инлайн-кнопок связанных с поливом растения
@bot.callback_query_handler(func=lambda call: call.data.startswith('water_'))
def handle_water_button_click(call):
    _, plant_name, _ = call.data.split("_")
    # добавить SQL запрос
    target_server_url = 'http://192.168.0.201:80/command'
    params = {'relay': '1'} 
    response = requests.get(target_server_url, params=params)
    print(response.text)
    
    bot.send_message(call.message.chat.id, f'Растение {plant_name} успешно полито')
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)

# Обработчик инлайн-кнопок связанных с просмотром информации о растении
@bot.callback_query_handler(func=lambda call: call.data.startswith('info_'))
def handle_water_button_click(call):
    _, _, plant_id = call.data.split("_")
    plant = PSQL.get_plant(plant_id, ['name', 'soil_humidity', 'relay_number'])
    if plant:
        name = plant[0]
        humidity = plant[1] if plant[1] else 'Неизвестно'
        relay = plant[2]
        answer = f"<b>Название растения:</b> <code>{name}</code>\n" \
                  f"<b>Влажность почвы:</b> <code>{humidity}</code>\n" \
                  f"<b>Номер реле:</b> <code>{relay}</code>"
        bot.send_message(call.message.chat.id, answer, parse_mode='HTML')
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)

bot.polling()
