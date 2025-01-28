# ai.py
import google.generativeai as genai
import time
import os

from google.generativeai.types.generation_types import GenerateContentResponse

from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")


def semantic_correction(example: str, user_input: str) -> str:
    return f"El usuario está intentando registrar una reserva. Para hacerlo tenía que escribir sus datos como muestra el ejemplo:\n{example}\n Sin embargo escribió:\n{user_input}\nSugiere donde pudo haberse equivocado de forma breve. No saludes, esto es parte de una conversación ya iniciada."


def ask_to_ai(question, context, personality):
    try:
        prompt = (
            f"Your personality: {personality}. Siempres respondes de manera muy breve\n\n"
            f"Contexto: {context}\n\n"
            f"Pregunta: {question}"
        )
        response: GenerateContentResponse = model.generate_content(
            {"role": "user", "parts": [prompt]}
        )
        return response.text
    except Exception as e:
        print(e)
        return "Lo siento, ocurrió un error al generar la respuesta. Por favor, intenta nuevamente más tarde."
