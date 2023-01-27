from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    date_check_in = State()
    date_check_out = State()
    city = State()
    hotels_count = State()
    hotel_photos_count = State()
    wait_choice = State()
    price = State()
    distance = State()
