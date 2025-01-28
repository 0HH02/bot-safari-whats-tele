#bot.py
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import json
from datetime import datetime


# import locales
from new_event import procesar_nombre_evento
from reserva import procesar_reserva
from config import TOKEN
from utils import (
    reply_command_list,
    procesar_download,
    get_eventos_disponibles,
    procesar_modificar_evento,
    procesar_info,
    procesar_eliminar_evento,
    cancelar,
    procesar_cerrar_evento,
    mostrar_lista_dispo,
    show_all_info_disonible,
    find_user,
    get_last_event,
)
from ai import ask_to_ai

bot = telebot.TeleBot(TOKEN)

# variables globales
admin = (
    {}
)  # para poder realizar operaciones despues de tocar /samuadmin, antes no podran usar los comados


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        if call.data == "reservar":
            # cuando toca el botón inline reservar...
            # comprobar el numero de promotor
            disponibles, ids = get_eventos_disponibles(data, "reservar")
            if len(disponibles) != 0:
                bot.send_message(call.message.chat.id, disponibles)
                bot.register_next_step_handler(call.message, procesar_reserva, ids, bot)
            else:
                bot.send_message(call.message.chat.id, "No hay evnetos disponibles")
        elif call.data == "flayer":
            # cuando toca el botón flayer.
            show_all_info_disonible(call.message, bot)
        elif call.data == "modificar_reserva":
            m = InlineKeyboardMarkup()
            m.add(InlineKeyboardButton("Cancelar", callback_data="cancelar"))
            m.add(InlineKeyboardButton("Modificar", callback_data="modificar"))
            bot.send_message(
                call.message.chat.id,
                "¿Desea modificar o cancelar la reserva?",
                reply_markup=m,
            )

        elif call.data == "cancelar":
            # logica para cancelar la reserva
            cancelar(bot, call.message)

        elif call.data == "modificar":
            # logica para modificar la reserva
            bot.send_message(call.message.chat.id, "Nueva Capacidad a poner?")


@bot.message_handler(commands=["start"])
def start_message(message):
    reply_command_list(message, bot)


@bot.message_handler(commands=["admin"])
def samuadmin(message):
    admin[message.chat.id] = True
    bot.send_message(
        message.chat.id,
        "/downloadlista -> lista reservas\n\n/newevent -> Nuevo Evento\n\n/eliminarEvento -> Borrar Evento\n\n/editevent -> Modificar Capacidad Evento\n\n/cerrarEvento -> Cerrar Capacidad Evento\n\n/infoEvento -> Informaciones del Evento\n\n/estadisticas -> Mostrar estadísticas",
    )


# funciones para crear el evento (hace las pregutas)
@bot.message_handler(commands=["newevent"])
def nombre_evento(message):
    try:
        if admin.get(message.chat.id):
            bot.send_message(message.chat.id, "¿Cuál es el nombre del evento?")
            bot.register_next_step_handler(message, procesar_nombre_evento, bot)
        else:
            reply_command_list(message, bot)
    except:
        reply_command_list(message, bot)


def enviar_estadisticas(message):
    import matplotlib.pyplot as plt

    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
    events = [event["name"] for event in data["Events"]]
    reservations_count = [len(event["reservations"]) for event in data["Events"]]

    # Envia una foto
    plt.figure(figsize=(8, 6))
    plt.bar(events, reservations_count)
    plt.xlabel("Events")
    plt.ylabel("Number of Reservations")
    plt.title("Number of Reservations per Event")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart to a file
    file_path = "Reservations_per_Event.png"
    plt.savefig(file_path)
    plt.close()

    bot.send_photo(chat_id=message.chat.id, photo=open(file_path, "rb"))


def calculate_age(ci):
    # Extract year, month, and day from CI
    year = int("19" + ci[:2]) if ci[0] in "01" else int("20" + ci[:2])
    month = int(ci[2:4])
    day = int(ci[4:6])
    birth_date = datetime(year, month, day)
    today = datetime.now()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


@bot.message_handler(commands=["estadisticas"])
def estadisticas(message):
    try:
        if admin.get(message.chat.id):
            enviar_estadisticas(message)
        else:
            reply_command_list(message, bot)
    except:
        reply_command_list(message, bot)


@bot.message_handler(commands=["downloadlista"])
def downloadlista(message):
    try:
        if admin.get(message.chat.id):
            # mostrar el numero de eventos y hacer la logica con el json para descargar el csv
            mostrar_lista_dispo(
                bot, procesar_download, "descargar lista invitados", message
            )
        else:
            reply_command_list(message, bot)
    except:
        reply_command_list(message, bot)


@bot.message_handler(commands=["editevent"])
def modificar_evento(message):
    try:
        if admin.get(message.chat.id):
            mostrar_lista_dispo(bot, procesar_modificar_evento, "modificar", message)
        else:
            reply_command_list(message, bot)
    except:

        reply_command_list(message, bot)


@bot.message_handler(commands=["eliminarEvento"])
def eliminar_evento(message):
    try:
        if admin.get(message.chat.id):
            mostrar_lista_dispo(
                bot, procesar_eliminar_evento, "eliminar", message, True
            )
        else:
            reply_command_list(message, bot)
    except:
        reply_command_list(message, bot)


@bot.message_handler(commands=["infoEvento"])
def infoEvento(message):
    try:
        if admin.get(message.chat.id):
            mostrar_lista_dispo(bot, procesar_info, "ver info", message)
        else:
            reply_command_list(mesasge, bot)

    except:
        reply_command_list(message, bot)


@bot.message_handler(commands=["cerrarEvento"])
def cerrarEvento(message):
    try:
        # solo se activa si toco /samuadmin primero
        if admin.get(message.chat.id):
            mostrar_lista_dispo(bot, procesar_cerrar_evento, "cerrar", message)
        else:
            reply_command_list(message, bot)
    except:
        reply_command_list(message, bot)


@bot.message_handler(content_types=["text"])
def text(message):
    reply_command_list(message, bot)


if __name__ == "__main__":
    bot.infinity_polling()
