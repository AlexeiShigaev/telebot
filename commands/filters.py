import telebot
from telebot import types, AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter

calendar_day = CallbackData("date_of", "year", "month", "day", prefix="calendar_day")
calendar_factory = CallbackData("date_of", "year", "month", prefix="calendar")
calendar_zoom = CallbackData("date_of", "year", prefix="calendar_zoom")
set_date = CallbackData("date_of", "year", "month", "day", prefix="set_date")
choice_city = CallbackData("date_of", "year", "month", "day", prefix="set_date")


class CalendarSetDayCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_day_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class CalendarDayCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_day_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class CalendarCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class CalendarZoomCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_zoom_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


def bind_filters(bot: telebot.TeleBot):
    bot.add_custom_filter(CalendarSetDayCallbackFilter())
    bot.add_custom_filter(CalendarDayCallbackFilter())
    bot.add_custom_filter(CalendarCallbackFilter())
    bot.add_custom_filter(CalendarZoomCallbackFilter())
