import telebot
import requests
import json
import config
from config import currencies
from extensions import ConvertException

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start", "help"])
def help_user(message: telebot.types.Message):
    text = "Чтобы начать работу введите команду в следующем формате:\n<имя валюты> /\n<в какую валюту перевести> /\n<количество переводимой валюты>\nСписок всех доступных валют: /currencies"
    bot.reply_to(message, text)


@bot.message_handler(commands=["currencies"])
def get_currencies(message: telebot.types.Message):
    text = "Доступные валюты:"
    for key in currencies.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)


@bot.message_handler(content_types=["text"])
def convert(message: telebot.types.Message):
    values = message.text.split(' ')
    if len(values) > 3:
        raise ConvertException("Слишком много параметров")
    elif len(values) < 3:
        raise ConvertException("Слишком мало параметров")
    quote, base, amount = values
    if quote == base:
        raise ConvertException(f"Нельзя конвертировать {quote} в {base}!")
    quote_ticker, base_ticker = currencies[quote], currencies[base]
    try:
        quote_ticker = currencies[quote]
    except KeyError:
        raise ConvertException(f"Не удалось обработать валюту: {quote}")
    try:
        base_ticker = currencies[base]
    except KeyError:
        raise ConvertException(f"Не удалось обработать валюту: {base}")
    try:
        amount = float(amount)
    except ValueError:
        raise ConvertException(f"Не удалось обработь количество: {amount}")

    r = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}")
    total_base = json.loads(r.content)[currencies[base]]
    text = f"Цена {amount} {quote} в {base} - {total_base * amount}"

    bot.send_message(message.chat.id, text)


bot.infinity_polling()
