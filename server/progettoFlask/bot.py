## pyTelegramBotAPI dependency

import os

import telebot

from utils import check_auth, send_report

BOT_TOKEN = '5701459800:AAG5zIMCLbL-14go0kgR7feZh6rRUCGkfi4'

bot = telebot.TeleBot(BOT_TOKEN)

authUsers = []

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Benvenuto. Scegli /auth per l'autenticazione")


@bot.message_handler(commands=['auth'])
def sign_handler(message):
    text = "Inserisci la tua secret key"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, auth_handler)


def auth_handler(message):
    key = message.text
    response = check_auth(key)
    
    if response['status'] == 'AUTHENTICATED': 
        authUsers.append(message.from_user.id)
        text = 'Sei stato autenticato! Seleziona /receivelastreport per ottenere l\'ultimo report dei consumi energetici'
        bot.send_message(
			message.chat.id, text, parse_mode="Markdown")
    else: 
        text = 'Non autorizzato.'
        bot.send_message(
			message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['receivelastreport'])
def sign_handler(message):
    if message.from_user.id in authUsers:
        response = send_report()
        if response.status_code == 200: bot.send_message(message.chat.id, 'L\'ultimo report mensile dei consumi è: ' + response.json()['report'], parse_mode="Markdown")
        else: bot.send_message(message.chat.id, 'ERROR ' + response.status_code , parse_mode="Markdown")
    else: bot.send_message(message.chat.id, 'Utente non autorizzato.' , parse_mode="Markdown")

bot.infinity_polling()
