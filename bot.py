import os
import logging
import yfinance as yf
import pandas as pd
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Configurações
TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))

# Inicializar bot
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Configurar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def verificar_cruzamento_ema(ticker="AAPL", periodo_curta=9, periodo_longa=21):
    df = yf.download(ticker, period="3mo", interval="1d")
    df["EMA_curta"] = df["Close"].ewm(span=periodo_curta, adjust=False).mean()
    df["EMA_longa"] = df["Close"].ewm(span=periodo_longa, adjust=False).mean()
    cruzamento = df["EMA_curta"].iloc[-2] < df["EMA_longa"].iloc[-2] and df["EMA_curta"].iloc[-1] > df["EMA_longa"].iloc[-1]
    return cruzamento

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot de alerta de cruzamento de EMAs ativo!")

def alerta(update, context):
    ticker = context.args[0] if context.args else "AAPL"
    if verificar_cruzamento_ema(ticker):
        context.bot.send_message(chat_id=USER_ID, text=f"🚨 Cruzamento de EMAs detectado em {ticker}!")
    else:
        context.bot.send_message(chat_id=USER_ID, text=f"Nenhum cruzamento de EMAs em {ticker}.")

# Handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("alerta", alerta))

# Iniciar bot
updater.start_polling()
updater.idle()
