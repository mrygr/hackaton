import json
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from sentence_transformers import SentenceTransformer, util

# Modelo para similitud de preguntas
modelo = SentenceTransformer('distiluse-base-multilingual-cased')


# Cargar preguntas frecuentes
try:
    with open("faqs2.json", "r", encoding="utf-8") as f:
        faqs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error cargando FAQs: {e}")
    faqs = {}

preguntas = list(faqs.keys())
respuestas = list(faqs.values())
vectores_preguntas = modelo.encode(preguntas, convert_to_tensor=True)

# Catálogo de productos sin emojis
catalogo_productos = {
    "automatizacion": "Automatización: Ofrecemos automatización de procesos industriales usando sensores, PLCs, robots y más para optimizar tu operación.",
    "software": "Desarrollo de Software: Creamos software a medida para escritorio, web, móvil y sistemas embebidos.",
    "datos": "Análisis de Datos: Realizamos visualizaciones, modelos predictivos y consultoría estadística.",
    "hardware": "Desarrollo de Hardware: Diseñamos PCBs, sistemas embebidos y prototipos industriales personalizados.",
    "mantenimiento": "Mantenimiento Industrial: Preventivo, correctivo y predictivo para asegurar la continuidad operativa.",
    "parqueaderos": "Parqueaderos Automáticos: Sistemas de control de acceso, lectura de placas (ANPR) y gestión automática.",
    "nfc": "Tarjetas NFC: Tarjetas físicas con NFC y códigos QR para pagos, control de acceso y gestión de usuarios."
}

# Función de respuesta semántica
def responder_pregunta(pregunta_usuario):
    vector_usuario = modelo.encode(pregunta_usuario, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(vector_usuario, vectores_preguntas)[0]
    indice_max = similitudes.argmax()
    puntaje = similitudes[indice_max].item()

    if puntaje > 0.4:
        return respuestas[indice_max]
    else:
        return "Lo siento, no entendí tu pregunta. Puedes intentar reformularla o usar /productos para ver lo que ofrecemos."

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, soy tu asistente de INGE-LEAN. Puedes hacerme una pregunta o usar /productos para ver lo que ofrecemos."
    )

# Comando /productos
async def mostrar_productos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Automatización", callback_data="automatizacion")],
        [InlineKeyboardButton("Software", callback_data="software")],
        [InlineKeyboardButton("Análisis de Datos", callback_data="datos")],
        [InlineKeyboardButton("Hardware", callback_data="hardware")],
        [InlineKeyboardButton("Mantenimiento", callback_data="mantenimiento")],
        [InlineKeyboardButton("Parqueaderos", callback_data="parqueaderos")],
        [InlineKeyboardButton("Tarjetas NFC", callback_data="nfc")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¿Qué producto te interesa?", reply_markup=reply_markup)

# Manejar selección de producto
async def producto_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    producto = query.data
    descripcion = catalogo_productos.get(producto, "Lo siento, no tengo información sobre ese producto.")

    keyboard = [
        [InlineKeyboardButton("Quiero cotizar", url="https://ingelean.com/contact/")],
        [InlineKeyboardButton("Volver a productos", callback_data="volver_productos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=descripcion, reply_markup=reply_markup)

# Manejar volver a productos desde botón
async def manejar_volver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "volver_productos":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Automatización", callback_data="automatizacion")],
            [InlineKeyboardButton("Software", callback_data="software")],
            [InlineKeyboardButton("Análisis de Datos", callback_data="datos")],
            [InlineKeyboardButton("Hardware", callback_data="hardware")],
            [InlineKeyboardButton("Mantenimiento", callback_data="mantenimiento")],
            [InlineKeyboardButton("Parqueaderos", callback_data="parqueaderos")],
            [InlineKeyboardButton("Tarjetas NFC", callback_data="nfc")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("¿Qué producto te interesa?", reply_markup=reply_markup)

# Manejar mensajes de texto
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto_usuario = update.message.text.lower()
        respuesta = responder_pregunta(texto_usuario)
        await update.message.reply_text(respuesta)
    except Exception as e:
        await update.message.reply_text("Ocurrió un error procesando tu mensaje.")
        print(f"Error en responder(): {e}")

# Función principal
def main():
    TOKEN = "8219869316:AAHgjkGecZhvQXEMEedm36OASor0qzNfdJc"  

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("productos", mostrar_productos))
    app.add_handler(CallbackQueryHandler(producto_seleccionado, pattern="^(automatizacion|software|datos|hardware|mantenimiento|parqueaderos|nfc)$"))
    app.add_handler(CallbackQueryHandler(manejar_volver, pattern="^volver_productos$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot en funcionamiento...")
    app.run_polling()

if __name__ == "__main__":
    main()
