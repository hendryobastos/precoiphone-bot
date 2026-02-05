import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN não encontrado")

ofertas = []

def extrair_oferta(texto):
    texto = texto.lower()

    modelo = None
    for n in ["11","12","13","14","15"]:
        if f"iphone {n}" in texto:
            modelo = f"iPhone {n}"

    if not modelo:
        return None

    if "pro max" in texto:
        modelo += " Pro Max"
    elif "pro" in texto:
        modelo += " Pro"
    elif "plus" in texto:
        modelo += " Plus"

    arm = "N/I"
    for g in ["128gb","256gb","512gb"]:
        if g in texto:
            arm = g.upper()

    match = re.search(r'(\d{4,5})', texto)
    if not match:
        return None

    preco = int(match.group(1))
    return modelo, arm, preco

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot ativo. Envie ofertas de iPhone.")

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    oferta = extrair_oferta(update.message.text)
    if not oferta:
        return

    modelo, arm, preco = oferta
    hoje = datetime.now().date()
    ofertas.append((modelo, arm, preco, hoje))

    precos = [o[2] for o in ofertas if o[0]==modelo and o[1]==arm and o[3]==hoje]

    if preco == min(precos):
        msg = f"🔥 MELHOR PREÇO DO DIA\n{modelo} {arm}\nR$ {preco}"
    else:
        msg = f"📱 Oferta registrada\n{modelo} {arm}\nR$ {preco}"

    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analisar))
app.run_polling()
