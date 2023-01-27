import json
import sys
from datetime import datetime, timedelta
from commands.states import UserState
from commands.commons import *
from commands.keyboards import generate_numbers_buttons, generate_cities_buttons
from telebot.types import CallbackQuery, Message, InputMediaPhoto
from api.hotels import find_city, find_hotels, find_hotel_photos
from config import MAX_HOTELS, MAX_HOTEL_PHOTOS
from database.sqlite3interface import save


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def commands_price(message: Message):
    """Реагирует на команду lowprice. Запускает цепочку колбэков, пока не получим пакет данных для запроса"""
    logger.info('Получена команда {}\n{}'.format(message.text[1:], message))

    bot.set_state(message.from_user.id, UserState.date_check_in, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1:]
    """Сохранили команду в стейт. Зададим стартовые значения, для прогрессивных (ленивых).
    Если никаких данных еще не было введено - в data только один элемент - команда"""
    check_in = datetime.now() + timedelta(days=2)
    check_out = check_in + timedelta(days=3)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if len(data) <= 1:
            data.update({'date_check_in': check_in.strftime('%d.%m.%Y'),
                         'date_check_out': check_out.strftime('%d.%m.%Y'), 'city': 'Берлин',
                         'hotels_count': '3', 'hotel_photos_count': '4', 'city_gaiaId': '536',
                         'min_price': '10', 'max_price': '160',
                         'min_distance': '1', 'max_distance': '6'})
    """Отрисовка главного меню для сбора данных к запросу"""
    mess = bot.send_message(message.chat.id, gen_info(message.from_user.id, message.chat.id),
                            reply_markup=generate_base_menu(message.text[1:]), parse_mode='HTML')
    logger.info('{}: Отправлено send_message:\n{}'.format(message.text[1:], mess))


@bot.callback_query_handler(func=lambda callback: callback.data == 'city')
def button_city_handler(call: CallbackQuery):
    """Нажата кнопка основного меню для выбора города. Приглашаем ввести город для поиска"""
    logger.info('Запрос на ввод города')
    bot.set_state(call.from_user.id, UserState.city, call.message.chat.id)
    """При этом убираю главное меню, чтоб не было соблазна потыкать лишнего"""
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, 'Отправьте сообщением искомый город\nнапример Berlin')


@bot.message_handler(state=UserState.city)
def input_city_handler(message: Message):
    """Получено сообщением имя города для поиска"""
    logger.info('Ввели город: {}, все сообщение в отладку:{}\n'.format(message.text, message))
    """Дадим понять что торопиться не следует"""
    mess = bot.send_message(
        message.chat.id, 'Ожидайте, запрос выполняется\n{}'.format(message.text), reply_markup=None
    )
    """Делаем запрос города. если что-то нашли то выдаем варианты для уточнения какой именно город"""
    cities = find_city(message.text)
    if len(cities) > 0:
        logger.info('Найдены города\n{}'.format(cities))
        """Заменяем ожидалку результатами поиска. Результат может быть из нескольких вариантов."""
        bot.edit_message_text('Результат поиска:\nВыберите искомый город.', mess.chat.id, mess.id)
        ret = bot.edit_message_reply_markup(
            mess.chat.id, mess.id, reply_markup=generate_cities_buttons(cities)
        )
        logger.debug('отправляем кнопки для выбора нужного города\n{}'.format(ret))
        """Теперь будем ждать подтверждения - UserState.wait_choice"""
        bot.set_state(message.from_user.id, UserState.wait_choice, message.chat.id)
    else:
        bot.edit_message_text('Ничего не смог найти.\nПопробуйте сменить раскладку\n' +
                              'Города РФ не обслуживаются данным сервисом', mess.chat.id, mess.id)
        """Возвращаем главное меню"""
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            bot.send_message(message.chat.id, gen_info(message.from_user.id, message.chat.id),
                             reply_markup=generate_base_menu(data['command']), parse_mode='HTML')
        logger.info('Не нашли город'.format(message.text))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('set_city'))
def set_city_handler(call: CallbackQuery):
    """Нажата кнопка в списке найденных городов. Фиксируем."""
    logger.info('с городом решили: {}'.format(call.message))
    """Выделим отдельно город и его код для сохранения."""
    lst = call.data.split(':')
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = lst[1]
        data['city_gaiaId'] = lst[2]
    """заменим сообщение и кнопки на главое меню"""
    bot.edit_message_text(
        gen_info(call.from_user.id, call.message.chat.id),
        call.message.chat.id, call.message.id, parse_mode='HTML'
    )
    """и кнопки тоже"""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.id,
            reply_markup=generate_base_menu(data['command'])
        )
    logger.info('Ждем уточнения дат запроса')


@bot.callback_query_handler(func=lambda callback: callback.data == 'hotel_photos_count')
def button_hotel_photo_count_handler(call: CallbackQuery):
    """Нажата кнопка в основном меню для ввода количества фотографий отелей"""
    logger.info('Запрос на ввод количества фото отелей в выборке')
    """Дальше будем ловить на UserState.hotel_photos_count"""
    bot.set_state(call.from_user.id, UserState.hotel_photos_count, call.message.chat.id)
    """Заменяем текст меню и клавиатуру"""
    bot.edit_message_text('Выберите количество фотографий отелей в выборке\n0 (ноль) означает без фотографий',
                          call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_numbers_buttons('hotel_photos_count')
    )


@bot.callback_query_handler(func=None, state=UserState.hotel_photos_count)
def input_hotel_photos_count_handler(call: CallbackQuery):
    """Нажата кнопка с цифрой количества фотографий отелей"""
    logger.info('Выбрали количество фотографий отелей: {}'.format(call.data))
    """выделяем количество и сохраняем в стейт"""
    key, value = call.data.split(':')
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data[key] = str(min(int(value), int(MAX_HOTEL_PHOTOS)))
    bot.edit_message_text(
        gen_info(call.from_user.id, call.message.chat.id),
        call.message.chat.id, call.message.id, parse_mode='HTML'
    )
    """Кнопки основного меню"""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.id,
            reply_markup=generate_base_menu(data['command'])
        )
    bot.set_state(call.from_user.id, UserState.wait_choice, call.message.chat.id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'hotels_count')
def button_hotels_count_handler(call: CallbackQuery):
    """Нажата кнопка в основном меню для выбора количества отелей в выборке"""
    logger.info('Запрос на ввод количества отелей в выборке')
    """Дальше будем ловить на UserState.hotels_count"""
    bot.set_state(call.from_user.id, UserState.hotels_count, call.message.chat.id)
    """Заменяем основное меню на текст запроса"""
    bot.edit_message_text('Выберите количество отелей в выборке', call.message.chat.id, call.message.id)
    """Клавиатуру заменяем на кнопочные цифры, чтоб не заморачиваться с проверками ввода"""
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.id,
        reply_markup=generate_numbers_buttons('hotels_count')
    )


@bot.callback_query_handler(func=None, state=UserState.hotels_count)
def input_hotels_count_handler(call: CallbackQuery):
    """Выбрали количество отелей в выборке"""
    logger.info('Выбрали количество отелей в выборке: {}'.format(call.data))
    """Выделяем"""
    key, value = call.data.split(':')
    """Фиксируем в стейт"""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data[key] = str(min(int(value), int(MAX_HOTELS)))
    """Возвращаем обратно основное меню"""
    bot.edit_message_text(
        gen_info(call.from_user.id, call.message.chat.id),
        call.message.chat.id, call.message.id, parse_mode='HTML'
    )
    """и клавиатуру основного меню"""
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.id,
            reply_markup=generate_base_menu(data['command'])
        )
    """Дальше может быть нажата, в общем, любая кнопка в основном меню."""
    bot.set_state(call.from_user.id, UserState.wait_choice, call.message.chat.id)


@bot.callback_query_handler(
    func=lambda cb: cb.data == 'query_lowprice' or
    cb.data == 'query_highprice' or
    cb.data == 'query_bestdeal'
)
def query_handler(call: CallbackQuery):
    """Все ли готово к запросу ?"""
    query_data = {}  # сюда скопируем стейт
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        d_format = '%d.%m.%Y'
        if (datetime.strptime(data['date_check_in'], d_format) >=
                datetime.strptime(data['date_check_out'], d_format)):
            bot.answer_callback_query(
                callback_query_id=call.id,
                text='Дата отъезда должна быть позже чем дата заезда.',
                show_alert=True
            )
            return
        else:
            """Теперь все нормально. Можно скопировать состояние и готовиться к запросу"""
            query_data.update(data)

    """Убираем основное меню с кнопками, чтоб не тыкали чего ни поподя."""
    bot.delete_message(call.message.chat.id, call.message.id)
    """И говорим что ведутся работы, терпите"""
    mess = bot.send_message(
        call.message.chat.id, 'Ожидайте, запрос выполняется', reply_markup=None
    )

    """Собственно, запрос отелей"""
    hotels = find_hotels(query_data)
    logger.debug('Получили список отелей. выдаем.')

    """Заменяем сообщение ожидания на информацию о запросе"""
    bot.edit_message_text(
        gen_info(call.from_user.id, call.message.chat.id), mess.chat.id, mess.id, parse_mode='HTML'
    )

    """Если hotels пустой, говорим ОЙ."""
    if len(hotels):
        """А если не пустой, то перечислим и выдадим отдельным сообщением каждый отель."""
        """Зафиксируем случившийся запрос в базе данных"""
        query_data.update({'query_date': datetime.now().strftime('%d.%m.%Y %H:%M')})
        save(str(call.from_user.id), json.dumps(query_data), json.dumps(hotels))
        """Погнали по списку отелей в выдаче"""
        for hotel in hotels:
            # print('{} {}'.format(hotel['name'], hotel['hotel_img_url']))
            bot.send_message(
                call.message.chat.id,
                "Отель <b>{}</b>\n".format(hotel['name']) +
                "Расстояние от центра <b>{} км</b>\n".format(hotel['distance']) +
                "Цена <b>{}</b>\n".format(hotel['price']) +
                "Стоимость за период <b>{}</b>".format(hotel['price_total']),
                reply_markup=None, parse_mode='HTML'
            )
            """Теперь вытащим фотки этого отеля и отдадим в чат
            Значение hotel_photos_count == 0 означает что показывать фотки не нужно."""
            if int(query_data['hotel_photos_count']):
                """Скажем что нужно подождать и запросим фотки"""
                mess = bot.send_message(call.message.chat.id, 'Ждем фотографий...')
                list_photos = find_hotel_photos(hotel['id'], int(query_data['hotel_photos_count']))
                """удаляем сообщение об ожидании (фиксировали его в mess)"""
                bot.delete_message(mess.chat.id, mess.id)
                """Групповое фото, с подписями, отправляем."""
                try:
                    bot.send_media_group(
                        call.message.chat.id,
                        media=[InputMediaPhoto(media=el['url'],
                                               caption=el['desc'].replace('«', '').replace('»', '')
                                               ) for el in list_photos]
                    )
                except Exception as ex:
                    tb = sys.exc_info()[2]
                    logger.error('\nПри отправке фотографий произошло исключение\n{}'.format(
                        str(ex.with_traceback(tb)))
                    )
                    bot.send_message(call.message.chat.id, 'Не удалось получить фотографии')
        bot.send_message(call.message.chat.id, 'Запрос завершен.')
        logger.info('Запрос завершен.\n{}'.format(hotels))
    else:
        bot.send_message(
            call.message.chat.id,
            'По вашему запросу ничего не найдено\nПопробуйте через 5 минут\n/help',
            reply_markup=None
        )
