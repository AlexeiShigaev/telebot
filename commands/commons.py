from datetime import datetime, date
from telebot.types import CallbackQuery
from commands.filters import calendar_factory, calendar_zoom, calendar_day, set_date
from commands.keyboards import generate_calendar_days, generate_calendar_months, generate_base_menu
from loader import bot
from logs import logger

commands_set = {
    'help': 'описание бота',
    'lowprice': 'Запрос самых дешевых отелей',
    'highprice': 'Запрос самых дорогих отелей',
    'bestdeal': 'Запрос отелей, наиболее подходящих по цене и расположению от центра',
    'history': 'Показать историю запросов'
}

about: str = ''.join('/{} - {}\n'.format(key, value) for key, value in commands_set.items())


def gen_info(user_id: int, chat_id: int) -> str:
    """Берем данные состояния, генерируем текст для пользователя. Будет вставлено в сообщение."""
    with bot.retrieve_data(user_id, chat_id) as data:
        msg = '<b>{}</b>\n'.format(commands_set[data['command']])
        msg += 'Город: <b>{}</b>\nДата заезда: <b>{}</b>\nДата отъезда: <b>{}</b>\n'.format(
            data['city'], data['date_check_in'], data['date_check_out'])
        if data['command'] == 'bestdeal':
            msg += 'Диапазон цен: <b>{} - {}</b>\n'.format(
                data['min_price'], data['max_price'])
            msg += 'Расстояние от центра: <b>{} - {}</b> (км)\n'.format(
                data['min_distance'], data['max_distance'])
        msg += 'Количество отелей в выборке: <b>{}</b>\nКоличество фото отеля: <b>{}</b>'.format(
            data['hotels_count'], data['hotel_photos_count'])
    return msg


@bot.callback_query_handler(func=lambda c: c.data == 'no_action')
def calendar_bad_day_handler(call: CallbackQuery):
    """Заглушка; если в календаре тыкают в пустой день."""
    logger.debug('Пользователь не то тыкает в календаре {}\n{}'.format(call.data, call))


@bot.callback_query_handler(func=lambda c: c.data == 'date_check_in' or c.data == 'date_check_out')
def calendar_handler(call: CallbackQuery):
    """Этап уточнения дат заезда и выезда. Выводим календарь, заменяя кнопки основного меню."""
    logger.debug('Получен выбор пользователя: {}\n{}'.format(call.data, call))
    now = date.today()
    ret = bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_calendar_days(date_of=call.data, year=now.year, month=now.month, day=now.day)
    )
    logger.debug('Отправлено edit_message_reply_markup:\n{}'.format(ret))


@bot.callback_query_handler(func=None, calendar_day_config=calendar_day.filter())
def calendar_day_action_handler(call: CallbackQuery):
    """При выборе даты пользователь может неоднократно ткнуть в разные дни.
    Перерисовываем календарь. Выделяется точкой в календаре выбранный день."""
    logger.debug('Реагируем на выбор дня: {}\n{}'.format(call.data, call))

    callback_data: dict = calendar_day.parse(callback_data=call.data)
    date_of, year = callback_data['date_of'], int(callback_data['year'])
    month, day = int(callback_data['month']), int(callback_data['day'])

    ret = bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_calendar_days(date_of=date_of, year=year, month=month, day=day)
    )
    logger.debug('Отправлено edit_message_reply_markup:\n{}'.format(ret))


@bot.callback_query_handler(func=None, calendar_config=calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery):
    """Долговременное планирование подразумевает выбор месяца и года. Перерисовываем календарь."""
    logger.debug('Реагируем на выбор месяца и года: {}\n{}'.format(call.data, call))

    callback_data: dict = calendar_factory.parse(callback_data=call.data)
    date_of, year, month = callback_data['date_of'], int(callback_data['year']), int(callback_data['month'])

    ret = bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_calendar_days(date_of=date_of, year=year, month=month)
    )
    logger.debug('Отправлено edit_message_reply_markup:\n{}'.format(ret))


@bot.callback_query_handler(func=None, calendar_config=set_date.filter())
def calendar_set_date_handler(call: CallbackQuery):
    """Одну из дат ввели. Фиксируем.
    Проверка: дата должна быть в будущем времени!"""
    logger.info('Одну из дат ввели. Фиксируем состояние: {}\n{}'.format(call.data, call))

    data = call.data.split(':')
    check_date = datetime(int(data[2]), int(data[3]), int(data[4]))

    if datetime.now() >= check_date:
        bot.answer_callback_query(
            callback_query_id=call.id,
            text='Зачем планировать прошлое?!\nПланируйте будущее :)',
            show_alert=True
        )
    else:
        """Фиксируем данные. В data[1] может быть lowprice или highprice"""
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as ret_data:
            ret_data[data[1]] = data[4] + '.' + data[3] + '.' + data[2]
        # Перерисовываем сообщение и кнопки
        bot.edit_message_text(
            gen_info(call.from_user.id, call.message.chat.id),
            call.message.chat.id, call.message.id, parse_mode='HTML'
        )
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as ret_data:
            bot.edit_message_reply_markup(
                call.message.chat.id, call.message.id,
                reply_markup=generate_base_menu(ret_data['command'])
            )


@bot.callback_query_handler(func=None, calendar_zoom_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery):
    """Перерисовываем календарь после выбора года"""
    callback_data: dict = calendar_zoom.parse(callback_data=call.data)
    date_of, year = callback_data['date_of'], int(callback_data['year'])

    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_calendar_months(date_of=date_of, year=year)
    )
