import re
from telebot import types

from keyboards import condition_keyboard
import SQL_request as PSQL

class PlantHandler:
    def __init__(self, bot):
        self.bot = bot
        self.name = None
        self.relay_number = None

    # Функция начинающая прецедент "добавление растения"
    def add_plant(self, call):
        self.bot.send_message(call.message.chat.id, '⬇️ Введите название растения ⬇️')
        # self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
        self.bot.register_next_step_handler(call.message, self.get_plant_name)

    # Функция обрабатывающая имя растения
    def get_plant_name(self, message):
        pattern = r"^[a-zA-Z0-9а-яА-Я ]+$"
        self.name = message.text  

        if re.match(pattern, self.name):
            self.bot.send_message(message.chat.id, '⬇️ Введите номер реле для растения ⬇️')
            self.bot.register_next_step_handler(message, self.get_relay_number)
        else:
            self.bot.send_message(message.chat.id, 'Имя растения может содержать только буквы и числа\n⬇️ Введите название растения ⬇️')
            self.bot.register_next_step_handler(message, self.get_plant_name)

    # Функция обрабатывающая номер реле
    def get_relay_number(self, message):
        pattern = r"^(10|[1-9])$"
        self.relay_number = message.text  

        if re.match(pattern, self.relay_number):
            self.bot.send_message(message.chat.id, 
                                  f'Параметры настроены верно? Проверьте, пожалуйста\nИмя растения: <code>{self.name}</code>\nНомер реле: <code>{self.relay_number}</code>',
                                  reply_markup=condition_keyboard("add_yes", "add_no"), 
                                  parse_mode='HTML')
            # self.bot.answer_callback_query(callback_query_id=message.chat.id, show_alert=False)
            
        else:
            self.bot.send_message(message.chat.id, 'Номер реле может быть только числом от 1 до 10 \n⬇️ Введите номер реле для растения ⬇️')
            self.bot.register_next_step_handler(message, self.get_relay_number)

    # Функция завершающая прецедент "добавление растения" (обрабатываем варинты да или нет)
    def add_confirmation(self, call):
        if call.data == 'add_yes':
            PSQL.add_plant(call.from_user.username, self.name, self.relay_number)
            self.bot.send_message(call.message.chat.id, f'Растение <code>{self.name}</code> успешно добавлено', parse_mode='HTML')
            return True

        elif call.data == 'add_no':
            self.bot.send_message(call.message.chat.id, f'Добавление растения отменено')

        else:
            self.bot.send_message(call.message.chat.id, 'Что-то пошло не так')

        
