from commands.lowhighprice import *


@bot.callback_query_handler(func=lambda callback: callback.data == 'price')
def button_price_handler(call: CallbackQuery):
    """Нажата кнопка основного меню для выбора диапазона цен. Приглашаем ввести цены для поиска"""
    logger.info('Запрос на ввод диапазона цен')
    bot.set_state(call.from_user.id, UserState.price, call.message.chat.id)
    """При этом убираю главное меню, чтоб не было соблазна потыкать лишнего"""
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, 'Отправьте сообщением желаемый диапазон цен\nнапример 10-150')


@bot.message_handler(state=UserState.price)
def input_price_handler(message: Message):
    """Получено сообщением диапазон цен"""
    logger.info('Ввели диапазон цен: {}, все сообщение в отладку:{}\n'.format(message.text, message))

    try:
        min_price, max_price = message.text.split('-')
        logger.debug('проверка {}-{}'.format(int(min_price), int(max_price)))
    except ValueError as ex:
        tb = sys.exc_info()[2]
        logger.debug(str(ex.with_traceback(tb)))
        bot.send_message(message.chat.id, 'Неверный формат, попробуйте еще раз\nНапример 10-160')
        return

    if int(min_price) >= int(max_price):
        bot.send_message(message.chat.id,
                         'Первое число должно быть меньше второго,\nпопробуйте еще раз\nНапример 10-160')
        return

    """Сохраняем введенные значения"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_price'] = min_price
        data['max_price'] = max_price

    """Возвращаем главное меню"""
    bot.send_message(
        message.chat.id,
        gen_info(message.from_user.id, message.chat.id),
        reply_markup=generate_base_menu('bestdeal'),
        parse_mode='HTML'
    )
    """Дальше пользователь может выбирать любые кнопки."""
    bot.set_state(message.from_user.id, UserState.wait_choice, message.chat.id)
    logger.info('Диапазон цен установлен: {}'.format(message.text))


@bot.callback_query_handler(func=lambda callback: callback.data == 'distance')
def button_distance_handler(call: CallbackQuery):
    """Нажата кнопка основного меню для выбора диапазона расстояний от центра."""
    logger.info('Запрос на ввод диапазона расстояний от центра')
    bot.set_state(call.from_user.id, UserState.distance, call.message.chat.id)
    """При этом убираю главное меню, чтоб не было соблазна потыкать лишнего"""
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(
        call.message.chat.id,
        'Отправьте сообщением желаемый диапазон расстояний от центра (км)\nнапример 1-8'
    )


@bot.message_handler(state=UserState.distance)
def input_distance_handler(message: Message):
    """Получено сообщением диапазон расстояний от центра"""
    logger.info('Ввели диапазон расстояний от центра: {}, все сообщение в отладку:{}\n'.format(message.text, message))

    try:
        min_distance, max_distance = message.text.split('-')
        logger.debug('проверка {}-{}'.format(int(min_distance), int(max_distance)))
    except ValueError as ex:
        tb = sys.exc_info()[2]
        logger.debug(str(ex.with_traceback(tb)))
        bot.send_message(message.chat.id, 'Неверный формат, попробуйте еще раз\nНапример 1-8')
        return

    if int(min_distance) >= int(max_distance):
        bot.send_message(
            message.chat.id,
            'Первое число должно быть меньше второго,\nпопробуйте еще раз\nНапример 1-8'
        )
        return

    """Сохраняем введенные значения"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['min_distance'] = min_distance
        data['max_distance'] = max_distance

    """Возвращаем главное меню"""
    bot.send_message(
        message.chat.id,
        gen_info(message.from_user.id, message.chat.id),
        reply_markup=generate_base_menu('bestdeal'),
        parse_mode='HTML'
    )
    """Дальше пользователь может выбирать любые кнопки."""
    bot.set_state(message.from_user.id, UserState.wait_choice, message.chat.id)
    logger.info('Диапазон расстояний от центра установлен: {}'.format(message.text))
