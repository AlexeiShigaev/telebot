import calendar
from datetime import date, timedelta
from commands.filters import calendar_factory, calendar_zoom, calendar_day, set_date
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

EMTPY_FIELD = 'no_action'

WEEK_DAYS = [calendar.day_abbr[i] for i in range(7)]
MONTHS = [(i, calendar.month_name[i]) for i in range(1, 13)]


def generate_calendar_days(date_of: str, year: int, month: int, day: int = 1) -> InlineKeyboardMarkup:
    """date_of передает check_in или check_out"""
    keyboard = InlineKeyboardMarkup(row_width=7)
    today = date.today()

    keyboard.add(
        InlineKeyboardButton(
            text="Дата: " + date(year=year, month=month, day=day).strftime('%d-%m-%Y'),
            callback_data=EMTPY_FIELD
        )
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=day_i,
            callback_data=EMTPY_FIELD
        )
        for day_i in WEEK_DAYS
    ])

    for week in calendar.Calendar().monthdayscalendar(year=year, month=month):
        week_buttons = []
        for day_i in week:
            day_name = ' '
            call_back = EMTPY_FIELD
            if day_i == day:
                day_name = '🔘'
            elif day_i > 0:
                day_name = str(day_i)
                call_back = calendar_day.new(date_of=date_of, year=year, month=month, day=day_i)
            week_buttons.append(
                InlineKeyboardButton(
                    text=day_name,
                    callback_data=call_back
                )
            )
        keyboard.add(*week_buttons)

    previous_date = date(year=year, month=month, day=day) - timedelta(days=31)
    next_date = date(year=year, month=month, day=day) + timedelta(days=31)

    keyboard.add(
        InlineKeyboardButton(
            text='Пред. мес.',
            callback_data=calendar_factory.new(date_of=date_of, year=previous_date.year, month=previous_date.month)
        ),
        InlineKeyboardButton(
            text='Выбрать год',
            callback_data=calendar_zoom.new(date_of=date_of, year=year)
        ),
        InlineKeyboardButton(
            text='След. мес.',
            callback_data=calendar_factory.new(date_of=date_of, year=next_date.year, month=next_date.month)
        ),
    )
    keyboard.add(
        InlineKeyboardButton(
            text='Подтвердить',
            callback_data=set_date.new(date_of=date_of, year=year, month=month, day=day)
        )
    )
    return keyboard


def generate_calendar_months(date_of: str, year: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=1, day=1).strftime('Год %Y'),
            callback_data=EMTPY_FIELD
        )
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=month,
            callback_data=calendar_factory.new(date_of=date_of, year=year, month=month_number)
        )
        for month_number, month in MONTHS
    ])
    keyboard.add(
        InlineKeyboardButton(
            text='Пред. год',
            callback_data=calendar_zoom.new(date_of=date_of, year=year - 1)
        ),
        InlineKeyboardButton(
            text='След. год',
            callback_data=calendar_zoom.new(date_of=date_of, year=year + 1)
        )
    )
    return keyboard


def generate_base_menu(command: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Выбрать город', callback_data='city')
    )
    keyboard.row(
        InlineKeyboardButton('Дата заезда', callback_data='date_check_in'),
        InlineKeyboardButton('Дата отъезда', callback_data='date_check_out')
    )
    if command == 'bestdeal':
        keyboard.row(
            InlineKeyboardButton('Диапазон цен', callback_data='price')
        )
        keyboard.row(
            InlineKeyboardButton('Диапазон расстояний от центра', callback_data='distance')
        )
    keyboard.row(
        InlineKeyboardButton('Количество отелей в выборке', callback_data='hotels_count')
    )
    keyboard.row(
        InlineKeyboardButton('Сколько фото отеля показывать', callback_data='hotel_photos_count')
    )
    keyboard.row(
        InlineKeyboardButton('Готово', callback_data='query_{}'.format(command))
    )
    return keyboard


def generate_numbers_buttons(prefix: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(15):
        buttons.append(
            InlineKeyboardButton(
                text=str(i),
                callback_data='{}:{}'.format(prefix, str(i))
            )
        )
    keyboard.add(*buttons)
    return keyboard


def generate_cities_buttons(cities: dict) -> InlineKeyboardMarkup:
    cities_buttons = []
    for gaiaId, city in cities.items():
        cities_buttons.append(
            InlineKeyboardButton(
                text=city,
                callback_data='set_city:{}:{}'.format(city.split(',')[0][:18], gaiaId)
            )
        )
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*cities_buttons)
    return keyboard


def generate_history_buttons(row_id: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Показать отели', callback_data='show:{}'.format(row_id)),
        InlineKeyboardButton('Удалить', callback_data='delete:{}'.format(row_id))
    )
    return keyboard
