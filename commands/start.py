from telebot.types import CallbackQuery, Message
from loader import bot
from logs import logger
from commands.commons import about


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    """Реагирует на команду start"""
    logger.info('Получена команда\n{}'.format(message.text))
    mess = bot.reply_to(message, "Привет, {}\n Я помогу подобрать отель\n{}".
                        format(message.from_user.first_name, about))
    logger.info('send_welcome: Отправлено:\n{}'.format(mess))


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message):
    """Дэфолтная реакция на любые сообщения"""
    logger.info('get_text_messages\n{}'.format(message))
    if message.text.lower().startswith('привет'):
        bot.reply_to(message, "Привет")
    elif message.text.startswith('/'):
        bot.reply_to(message, "Команда не реализована")
    else:
        bot.reply_to(message, "Моя-твоя-не-понимай\nКоманда /help")


@bot.callback_query_handler(func=None)
def default_handler(call: CallbackQuery):
    """Заглушка. Дэфолтный обработчик callback_query. Нужен больше для процесса разработки"""
    print('default_handler:' + call.data)
    print(call)
