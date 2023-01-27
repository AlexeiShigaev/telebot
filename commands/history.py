import json
from commands.keyboards import generate_history_buttons
from commands.bestdeal import *
from database.sqlite3interface import get_states, delete_row, get_query_res


@bot.message_handler(commands=['history'])
def commands_history(message: Message):
    logger.info('Получена команда {}\n{}'.format(message.text[1:], message))
    ret_data = get_states(str(message.from_user.id))
    if len(ret_data):
        for row in ret_data:
            state = json.loads(row[1])
            bot.send_message(
                message.chat.id,
                'Дата запроса: <b>{}</b>\nКоманда: <b>{}</b>\n'.format(
                    state['query_date'], commands_set[state['command']]) +
                'Город: <b>{}</b>\nДата заезда: <b>{}</b>\nДата отъезда: <b>{}</b>\n'.format(
                    state['city'], state['date_check_in'], state['date_check_out']),
                reply_markup=generate_history_buttons(str(row[0])), parse_mode='HTML'
            )
    else:
        bot.send_message(message.chat.id, 'История пуста')


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('delete'))
def delete_row_handler(call: CallbackQuery):
    logger.info('Попытка удалить элемент истории {}'.format(call.data))
    if delete_row(str(call.from_user.id), int(call.data.split(':')[1])):
        """Сообщаем что удалили."""
        bot.answer_callback_query(
            callback_query_id=call.id,
            text='Запись удалена из истории',
            show_alert=True
        )
        """Удаляем в том числе в чате"""
        bot.delete_message(call.message.chat.id, call.message.id)
    else:
        logger.info('Попытка удалить элемент истории {}\nЧто-то пошло не так'.format(call.data))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('show'))
def show_hotels_handler(call: CallbackQuery):
    logger.info('Покажем что нашлось в прошлый раз {}'.format(call.data))
    query_res = get_query_res(str(call.from_user.id), int(call.data.split(':')[1]))
    if len(query_res):
        state = json.loads(query_res[0][0])
        hotels = json.loads(query_res[0][1])
        bot.send_message(
            call.message.chat.id,
            'Дата запроса: <b>{}</b>\nКоманда: <b>{}</b>\n'.format(
                state['query_date'], commands_set[state['command']]) +
            'Город: <b>{}</b>\nДата заезда: <b>{}</b>\nДата отъезда: <b>{}</b>\n'.format(
                state['city'], state['date_check_in'], state['date_check_out']),
            parse_mode='HTML'
        )
        for hotel in hotels:
            bot.send_message(
                call.message.chat.id,
                "Отель <b>{}</b>\n".format(hotel['name']) +
                "Расстояние от центра <b>{} км</b>\n".format(hotel['distance']) +
                "Цена <b>{}</b>\n".format(hotel['price']) +
                "Стоимость за период <b>{}</b>".format(hotel['price_total']),
                reply_markup=None, parse_mode='HTML'
            )
    else:
        bot.send_message(call.message.chat.id, "Данных не найдено")
