
import os

import telebot

BOT_TOKEN = os.environ.get('6243526742:AAEx0fd738YXDL7WGWkaWIUF9tM6qBpY3o4')

bot = telebot.TeleBot(BOT_TOKEN)



@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


bot.infinity_polling()