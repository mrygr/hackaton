from transformers import pipeline

# Motor de NLP: puede usar modelo en español de HuggingFace
chatbot_nlp = pipeline("text-generation", model="mrm8488/GPT2-spanish", tokenizer="mrm8488/GPT2-spanish")

# Base de datos simple de preguntas frecuentes
faq = {
    "¿Cuál es tu nombre?": "Soy un chatbot creado para responder tus preguntas.",
    "¿Qué puedes hacer?": "Puedo ayudarte a resolver dudas frecuentes.",
    "¿Cómo funciona este sistema?": "Este sistema responde usando procesamiento de lenguaje natural.",
    "¿Cuál es tu horario de atención?": "Estoy disponible las 24 horas.",
    "¿Cómo contacto a soporte?": "Puedes enviar un correo a soporte@ejemplo.com.",
    "¿Ofrecen garantía?": "Sí, ofrecemos garantía de 1 año en todos los productos.",
    "¿Dónde están ubicados?": "Nuestra oficina principal está en Ciudad de México.",
    "¿Tienen servicio a domicilio?": "Sí, ofrecemos envíos a todo el país.",
    "¿Cómo rastreo mi pedido?": "Puedes rastrear tu pedido desde nuestra web ingresando tu número de orden.",
    "¿Aceptan pagos con tarjeta?": "Sí, aceptamos todas las tarjetas de crédito y débito."
}

def responder_faq(pregunta):
    for clave in faq:
        if clave.lower() in pregunta.lower():
            return faq[clave]
    return None

def chatbot():
    print("🤖 Chatbot activo. Escribe 'salir' para terminar.\n")
    
    while True:
        usuario = input("👤 Ingresa tu nombre de usuario: ")
        while True:
            mensaje = input(f"{usuario}: ")
            
            if mensaje.lower() == "salir":
                print("Chatbot: ¡Hasta luego!\n")
                break

            respuesta_faq = responder_faq(mensaje)
            if respuesta_faq:
                print(f"Chatbot: {respuesta_faq}")
            else:
                # Usa el modelo NLP si no encuentra respuesta en las FAQ
                respuesta = chatbot_nlp(mensaje, max_length=50, num_return_sequences=1)[0]['generated_text']
                print("Chatbot (NLP):", respuesta)