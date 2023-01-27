from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from commands.filters import bind_filters
from config import TOKEN

storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=storage)
bind_filters(bot)
bot.add_custom_filter(custom_filters.StateFilter(bot))
