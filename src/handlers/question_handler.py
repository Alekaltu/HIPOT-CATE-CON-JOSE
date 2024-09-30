from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from .start_handler import start
from datetime import datetime, timedelta
import calendar
from src.google_sheets.create_sheet import create_user_sheet
from src.google_sheets.update_values import update_user_data

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    
    if question == 'Iniciar simulación de hipoteca':
        response = "Para comenzar con la simulación de hipoteca, por favor proporciona tu nombre completo:"
        context.user_data['state'] = 'NOMBRE_COMPLETO'
        await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    elif not context.user_data.get('state'):
        # Si no hay estado, mostrar el botón para iniciar una nueva simulación
        keyboard = [['Iniciar simulación de hipoteca']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Para iniciar una simulación, pulsa el botón:", reply_markup=reply_markup)
        return
    elif context.user_data.get('state') == 'NOMBRE_COMPLETO':
        context.user_data['nombre_completo'] = question
        response = f"Gracias, {question}. Por ahora, solo podemos procesar simulaciones para compras individuales."
        context.user_data['compra_solo'] = True
        context.user_data['state'] = 'EDAD'
        await update.message.reply_text(response)
        await update.message.reply_text("¿Qué edad tienes?")
    elif context.user_data.get('state') == 'EDAD':
        try:
            edad = int(question)
            context.user_data['edad'] = edad
            response = "Entendido. ¿Estás trabajando actualmente?"
            keyboard = [['Sí'], ['No']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            context.user_data['state'] = 'TRABAJANDO'
            await update.message.reply_text(response, reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para tu edad:")
    elif context.user_data.get('state') == 'TRABAJANDO':
        context.user_data['trabajando'] = question.lower() == 'sí'
        if context.user_data['trabajando']:
            await send_calendar(update, context)
        else:
            response = "¿Tienes algún ingreso extra mensual? Si no tienes, escribe 0."
            context.user_data['state'] = 'INGRESOS_EXTRA'
            await update.message.reply_text(response)
    elif context.user_data.get('state') == 'YEAR_TRABAJO':
        try:
            year = int(question)
            context.user_data['year_trabajo'] = year
            response = "¿En qué mes comenzaste?"
            months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            keyboard = [[month] for month in months]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            context.user_data['state'] = 'MONTH_TRABAJO'
            await update.message.reply_text(response, reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("Por favor, selecciona un año válido.")
    elif context.user_data.get('state') == 'MONTH_TRABAJO':
        months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        if question in months:
            month = months.index(question) + 1
            year = context.user_data['year_trabajo']
            current_date = datetime.now()
            start_date = datetime(year, month, 1)
            months_worked = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            context.user_data['antiguedad_laboral'] = months_worked
            
            # Pasar al siguiente estado (tipo de contrato)
            response = "¿Qué tipo de contrato tienes?"
            keyboard = [
                ['Contrato Indefinido'],
                ['Contrato Temporal'],
                ['Contrato Formación en Alternancia'],
                ['Contrato Formativo para la Obtención de la Práctica Profesional']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            context.user_data['state'] = 'TIPO_CONTRATO'
            await update.message.reply_text(response, reply_markup=reply_markup)
        else:
            await update.message.reply_text("Por favor, selecciona un mes válido.")
    elif context.user_data.get('state') == 'TIPO_CONTRATO':
        context.user_data['tipo_contrato'] = question
        response = "¿Cuánto recibes de nómina mensualmente? Por favor, introduce solo el número sin símbolos."
        context.user_data['state'] = 'NOMINA'
        await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    elif context.user_data.get('state') == 'NOMINA':
        try:
            nomina = float(question)
            context.user_data['nomina'] = nomina
            response = "¿Tienes algún ingreso extra mensual? Si no tienes, escribe 0."
            context.user_data['state'] = 'INGRESOS_EXTRA'
            await update.message.reply_text(response)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para tu nómina mensual:")
    elif context.user_data.get('state') == 'INGRESOS_EXTRA':
        try:
            ingresos_extra = float(question)
            context.user_data['ingresos_extra'] = ingresos_extra
            response = "¿Tienes alguna deuda financiera (préstamos, etc.)? Responde Sí o No."
            keyboard = [['Sí'], ['No']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            context.user_data['state'] = 'TIENE_DEUDAS'
            await update.message.reply_text(response, reply_markup=reply_markup)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para tus ingresos extra:")
    elif context.user_data.get('state') == 'TIENE_DEUDAS':
        if question.lower() == 'sí':
            response = "¿Cuál es el monto total de tus deudas mensuales? Introduce solo el número."
            context.user_data['state'] = 'MONTO_DEUDAS'
            await update.message.reply_text(response)
        else:
            context.user_data['deudas'] = 0
            context.user_data['provincia'] = 'Madrid'
            response = "Por ahora, solo procesamos solicitudes para la provincia de Madrid. ¿Cuál es el precio de la vivienda en la que estás interesado? Introduce solo el número."
            context.user_data['state'] = 'PRECIO_VIVIENDA'
            await update.message.reply_text(response)
    elif context.user_data.get('state') == 'MONTO_DEUDAS':
        try:
            deudas = float(question)
            context.user_data['deudas'] = deudas
            context.user_data['provincia'] = 'Madrid'
            response = "Por ahora, solo procesamos solicitudes para la provincia de Madrid. ¿Cuál es el precio de la vivienda en la que estás interesado? Introduce solo el número."
            context.user_data['state'] = 'PRECIO_VIVIENDA'
            await update.message.reply_text(response)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para el monto de tus deudas:")
    elif context.user_data.get('state') == 'PRECIO_VIVIENDA':
        try:
            precio_vivienda = float(question)
            context.user_data['precio_vivienda'] = precio_vivienda
            response = "¿Cuánto ahorro quieres aportar a la compra? Introduce solo el número."
            context.user_data['state'] = 'AHORRO'
            await update.message.reply_text(response)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para el precio de la vivienda:")
    elif context.user_data.get('state') == 'AHORRO':
        try:
            ahorro = float(question)
            context.user_data['ahorro'] = ahorro
            await finalizar_recopilacion_datos(update, context)
        except ValueError:
            await update.message.reply_text("Por favor, introduce un número válido para tu ahorro:")
    elif context.user_data.get('state') == 'CONFIRMAR_MADRID':
        context.user_data['provincia'] = 'Madrid'
        response = "¿Cuál es el precio de la vivienda en la que estás interesado? Introduce solo el número."
        context.user_data['state'] = 'PRECIO_VIVIENDA'
        await update.message.reply_text(response)
    else:
        # Manejo de otros estados o preguntas no reconocidas
        response = ("Lo siento, no he entendido tu respuesta. "
                    "¿Quieres iniciar una simulación de hipoteca?")
        keyboard = [['Iniciar simulación de hipoteca'], ['Volver al menú principal']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(response, reply_markup=reply_markup)

    if question == 'Volver al menú principal':
        return await start(update, context)

async def finalizar_recopilacion_datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    spreadsheet_id = '1qWF-iOdviTQDfitgXnLgpe6d0esFHT--2X3h01jdma0'  # Asegúrate de que este ID sea correcto
    
    sheet_title = create_user_sheet(spreadsheet_id, user_id)
    if sheet_title:
        result = update_user_data(spreadsheet_id, sheet_title, context.user_data)
        print(f"Resultado de la actualización: {result}")
        mensaje_final = ("Gracias por usar el Bot de Hipotécate con Jose. "
                         "Tus datos han sido guardados y Jose se pondrá en contacto contigo lo antes posible. "
                         "¡Que tengas un buen día!")
    else:
        mensaje_final = ("Lo siento, ha habido un problema al guardar tus datos. "
                         "Por favor, intenta de nuevo más tarde o contacta con soporte.")

    await update.message.reply_text(mensaje_final)
    
    # Reiniciar el estado para una nueva simulación
    context.user_data.clear()
    
    # Mostrar el botón para iniciar una nueva simulación
    keyboard = [['Iniciar nueva simulación de hipoteca']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Si deseas realizar otra simulación, pulsa el botón:", reply_markup=reply_markup)

async def send_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    context.user_data['calendar_date'] = now
    await update.message.reply_text("Por favor, selecciona el año de inicio de tu trabajo actual:",
                                    reply_markup=create_calendar_keyboard(now, 'year'))

def create_calendar_keyboard(date, view):
    keyboard = []
    if view == 'year':
        current_year = datetime.now().year
        years = list(range(current_year, current_year - 60, -1))
        for i in range(0, len(years), 3):
            row = [InlineKeyboardButton(str(year), callback_data=f'year_{year}') for year in years[i:i+3]]
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("Anterior", callback_data="prev_years"),
                         InlineKeyboardButton("Siguiente", callback_data="next_years")])
    elif view == 'month':
        for i in range(1, 13, 3):
            row = [InlineKeyboardButton(calendar.month_abbr[j], callback_data=f'month_{j}') 
                   for j in range(i, min(i+3, 13))]
            keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('_')
    view = data[0]
    value = int(data[1]) if len(data) > 1 and data[1].isdigit() else 0
    
    date = context.user_data.get('calendar_date', datetime.now())
    
    if view == 'year':
        date = date.replace(year=value)
        await query.edit_message_text("Selecciona el mes:",
                                      reply_markup=create_calendar_keyboard(date, 'month'))
    elif view == 'month':
        date = date.replace(month=value)
        context.user_data['fecha_inicio_trabajo'] = date
        months_worked = (datetime.now().year - date.year) * 12 + datetime.now().month - date.month
        context.user_data['antiguedad_laboral'] = months_worked
        
        await query.edit_message_text(f"Has seleccionado la fecha: {date.strftime('%m/%Y')}")
        
        # Pasar al siguiente estado (tipo de contrato)
        response = "¿Qué tipo de contrato tienes?"
        keyboard = [
            ['Contrato Indefinido'],
            ['Contrato Temporal'],
            ['Contrato Formación en Alternancia'],
            ['Contrato Formativo para la Obtención de la Práctica Profesional']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.user_data['state'] = 'TIPO_CONTRATO'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=reply_markup)
    elif view in ['prev_years', 'next_years']:
        current_year = date.year
        new_year = current_year - 60 if view == 'prev_years' else current_year + 60
        date = date.replace(year=new_year)
        await query.edit_message_text("Selecciona el año de inicio de tu trabajo actual:",
                                      reply_markup=create_calendar_keyboard(date, 'year'))
    
    context.user_data['calendar_date'] = date