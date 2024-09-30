from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        #['Información general sobre hipotecas'],#
        ['Iniciar simulación de hipoteca'],
        #['Contactar con un asesor']#
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    message = (
        f"¡Hola {user.first_name}! Soy el bot de HIPOTÉCATE CON JOSE. "
        "Estoy aquí para ayudarte con información sobre hipotecas y realizar simulaciones. "
        "¿En qué puedo ayudarte hoy?"
    )
    await update.message.reply_text(message, reply_markup=reply_markup)