import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from src.handlers.start_handler import start
from src.handlers.question_handler import handle_question, calendar_handler

# Configura el logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Reemplaza 'TU_TOKEN' con el token real de tu bot
    application = Application.builder().token("7003566003:AAF-iYDenKEdWUVcExGMRdhmqol4YYSBFnQ").read_timeout(30).write_timeout(30).build()

    # Agrega handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_handler(CallbackQueryHandler(calendar_handler))

    # Inicia el bot
    application.run_polling(poll_interval=3)  # Ajusta el intervalo para reducir las llamadas

if __name__ == '__main__':
    main()