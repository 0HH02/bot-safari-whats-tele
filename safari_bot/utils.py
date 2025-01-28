import csv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import os
import re
from datetime import datetime
from ai import ask_to_ai

old_message = ""


def find_user(user_id):
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Users.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        if str(user_id) in data["Users"]:
            return data["Users"][str(user_id)]
        else:
            return None


def mostrar_lista_dispo(bot, funtion, action, message, all_events=False):
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        eventos_disponibles, ids = get_eventos_disponibles(data, action, all_events)
        # mostrar envetos disponibles
        if len(eventos_disponibles) != 0:
            bot.send_message(message.chat.id, eventos_disponibles)
            bot.register_next_step_handler(message, funtion, ids, bot)
        else:
            bot.send_message(message.chat.id, "No hay eventos disponibles")


def show_all_info_disonible(message, bot):
    bot.send_chat_action(message.from_user.id, "typing")

    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
    disponibles, ids = get_eventos_disponibles(data, "reservar")
    for i in ids:
        info, photo_path = info_show(i)
        bot.send_message(message.chat.id, info)
        for photo in photo_path:
            with open(
                os.path.join(os.path.dirname(__file__), "images", photo.split("/")[-1]),
                "rb",
            ) as img:
                bot.send_photo(message.chat.id, img)


def reply_command_list(mesagge, bot):
    bot.send_chat_action(mesagge.from_user.id, "typing")

    photo_path = os.path.join(os.path.dirname(__file__), "images", "piñito.jpg")

    new_user = {
        "Nombre": mesagge.from_user.first_name,
        "FechaUltimoEvento": None,
        "LugarUltimoEvento": None,
        "Amigos": [],
        "chat_id": mesagge.chat.id,
    }

    user = find_user(mesagge.chat.id) if find_user(mesagge.chat.id) else new_user

    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
    last_event = get_last_event(data)
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
    next_events, ids = get_eventos_disponibles(data, "reservar")
    global old_message
    if user["FechaUltimoEvento"] is None:
        welcome_message = ask_to_ai(
            "Te acaba de escribir un cliente nuevo al que le quieres vender una reservación para alguno de los eventos que ofreces. Lo llamarás por su nombre, Dile que justo la semana pasada estuvo muy genial el último evento que hicimos. Hazlo sentir que él también la podría pasar especial en uno de nuestros eventos y menciónale uno de ellos y pregúntale si quiere que le enseñes las ofertas que tienes preparadas para él. Si intentas decir una fecha interprétala y dila en lenguaje natural. Ejemplo: 12.12.2024 Dirías: el 12 de diciembre. Sé lo más breve posible pero engánchalo. Pon emojis",
            f"Nombre del cliente: {user['Nombre']}, Fecha actual: {str(datetime.now()).split()[0]}, Ultimo evento que hizo la empresa: {last_event}\nSiguientes Eventos: {next_events}\nDebe ser distinto de este mensaje: {old_message}\n",
            "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
        )
    else:
        welcome_message = ask_to_ai(
            "Te acaba de escribir un cliente al que le quieres vender una reservación para alguno de los eventos que ofreces. Lo llamarás por su nombre, si hace mucho que no reserva le harás un comentario insinuando que lo bien que la pasamos en el ultimo evento que hicimos, si reservó hace poco le dirás que esperas que la haya pasado muy bien (No menciones fechas), tiene que ser algo discreto, al estilo de: Hace mucho que no te vemos por acá, o si hace poco reservó: Veo que andas bien fiestero ultimamente, si fue con amigos incluyes a estos cuando des tu respuesta. Por último le preguntarás si quiere que le enseñes las ofertas que tienes preparadas para él. Sé lo más breve posible pero engánchalo. Pon emojis",
            f"Nombre del cliente: {user['Nombre']}, Ultima vez que reservó: {user['FechaUltimoEvento']}, Fecha actual: {str(datetime.now()).split()[0]}, Ultimo evento en el que participó: {user['LugarUltimoEvento']} Ultimo evento que se hizo: {last_event}\nSiguientes Eventos: {next_events}\nDebe ser distintp de este mensaje: {old_message}\n",
            "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
        )

    old_message = welcome_message
    with open(photo_path, "rb") as photo:
        caption = f"Soy Piñito 🍍 tu asistente virtual✨.\n{welcome_message}\n"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🎟 Reservar", callback_data="reservar"))
        markup.add(InlineKeyboardButton("🎆 Ofertas e info", callback_data="flayer"))
        # markup.add(
        #     InlineKeyboardButton("Modificar Reserva", callback_data="modificar_reserva")
        # )
        bot.send_photo(mesagge.chat.id, photo, caption, reply_markup=markup)


def buscar_indice_evento(data, id):
    for j, i in enumerate(data["Events"]):
        if i["id"] == id:
            return j


def info_show(id):
    sms = ""
    photo_path = []
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        for i in data["Events"]:
            if i["id"] == id:
                sms = f"Nombre del Evento: " + i["name"] + "\n"
                sms += f"Fecha: {i['date']}\n"
                sms += f"Lugar: {i['place']}"
                sms += f"Descripción: {i['description']}"
                photo_path = i["flayerPhoto"]
                break
    show_message = ask_to_ai(
        "Esta es la información de uno de los eventos que vas a estar vendiéndole a un cliente. Explica brevemente por qué es una gran idea ir. Las fechas dilas en lenguaje natural Ejemplo: 12.12.2024 Dirías: el 12 de diciembre. Pon emojis",
        sms,
        "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
    )
    return (show_message, photo_path)


def abrir_info_evento(id):
    sms = ""
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        for i in data["Events"]:
            if i["id"] == id:
                sms = "Evento #" + f"{id}" + " - " + i["name"] + "\n"
                sms += "capacidad: " + i["maxPlaces"] + "\n"
                sms += "Número de reservas: " + str(len(i["reservations"])) + "\n"
                break

    return sms


def enviar(message, bot):
    ruta_csv = os.path.join(os.path.dirname(__file__), "model", "lista.csv")
    with open(ruta_csv, "rb") as csvfile:
        bot.send_document(message.chat.id, csvfile)
        print("CSV enviado con éxito.")


def lista_invitados(data, id, message, bot):
    with open(
        os.path.join(os.path.dirname(__file__), "model", "lista.csv"),
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:
        # crear el csv y enviarlo con el bot
        index = buscar_indice_evento(data, id)

        if len(data["Events"][index]["reservations"]) != 0:
            fieldnames = data["Events"][index]["reservations"][0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data["Events"][index]["reservations"]:
                writer.writerow(row)
            csvfile.closed

        else:
            bot.send_message(message.chat.id, "No hay invitados para este evento")
            return
    enviar(message, bot)


def get_ultimo_id(data):
    ultimo_id = 0
    for i in data["Events"]:
        if int(i["id"]) > ultimo_id:
            ultimo_id = int(i["id"])
    return ultimo_id


def get_last_event(data):
    dia_actual = datetime.now()
    eventos_pasados = []
    for i in data["Events"]:
        try:
            fecha_evento = datetime.strptime(i["date"], "%d.%m.%Y")
            if fecha_evento and fecha_evento < dia_actual:
                eventos_pasados.append(i)
        except:
            print("Ocurrió un error con get_eventos_disponibles")

    # Ordenar eventos por fecha (más reciente primero)
    eventos_pasados.sort(
        key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"), reverse=True
    )

    # Obtener el evento más reciente
    if eventos_pasados:
        ultimo_evento = eventos_pasados[0]
        sms = (
            f"Nombre del Evento: {ultimo_evento['name']}\n"
            f"Fecha: {ultimo_evento['date']}\n"
            f"Lugar: {ultimo_evento['place']}\n"
            f"Descripción: {ultimo_evento['auxMessage']}\n"
        )
        return sms
    else:
        return "No hay eventos recientes que hayan pasado."


def get_eventos_disponibles(data, accion, all_events=False):
    dia_actual = datetime.now()
    sms = f"Eventos disponibles: \n\n¿Cuál es el número del evento que deseas {accion}?\n\n"
    ids = []
    ## retornar un string con el formato a mostar de los evetos disponiblesy una lista con los id de los eventos disponibles
    for i in data["Events"]:
        try:
            fecha_evento = datetime.strptime(i["date"], "%d.%m.%Y")
            if all_events or fecha_evento and fecha_evento >= dia_actual:
                sms += (
                    f'{i["id"]}   {i["name"]}\nFecha: {i["date"]}\nLugar: {i["place"]}'
                )
                ids.append(i["id"])
                sms += "\n\n"

        except:
            print("Ocurrió un error con get_eventos_disponibles")
    return sms, ids


################ cerrar evento ############
def procesar_cerrar_evento(message, ids, bot):
    if message.text in ids:
        pass
        # validar si el número es válido y cerrar el evento en el json
    else:
        bot.send_message(message.chat.id, "Seleccione un número de la lista.")
        bot.register_next_step_handler(message, procesar_cerrar_evento, ids)


########### download ###############
def procesar_download(message, ids, bot):
    if message.text in ids:
        # logica con el json para descargar el csv

        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
        ) as archivo:
            data = json.load(archivo)
            lista_invitados(data, message.text, message, bot)

    else:
        bot.send_message(message.chat.id, "Seleccione un número de la lista.")
        bot.register_next_step_handler(message, procesar_download, ids, bot)


########################## modificar ################
def procesar_modificar_evento(message, ids, bot):
    if message.text in ids:
        ## logiaca para modificar unn evento
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"),
            "r",
            encoding="utf-8",
        ) as date:
            data = json.load(date)
        bot.send_message(
            message.chat.id,
            "Nueva Capacidad a poner? ",
        )
        bot.register_next_step_handler(message, modificar, message.text, data, bot)

    else:
        bot.send_message(message.chat.id, "Seleccione un número de la lista.")
        bot.register_next_step_handler(message, procesar_modificar_evento, ids, bot)


def modificar(message, id, data, bot):
    try:
        if int(message.text):
            indice_evento_a_modificar = buscar_indice_evento(data, id)
            data["Events"][indice_evento_a_modificar]["maxPlaces"] = message.text

            json_update = json.dumps(data, indent=4)
            with open(
                os.path.join(os.path.dirname(__file__), "model", "Events.json"), "w"
            ) as arch:
                arch.write(json_update)
            bot.send_message(message.chat.id, "Evento modificado")
        else:
            bot.send_message(message.chat.id, "Escribe un número válido")
            bot.register_next_step_handler(message, modificar, id, data)
    except:
        bot.send_message(message.chat.id, "Escribe un número válido")
        bot.register_next_step_handler(message, modificar, id, data)


############################ eliminar ########################
def procesar_eliminar_evento(message, ids, bot):
    if message.text in ids:
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
        ) as archivo:
            data = json.load(archivo)
            data["Events"] = [
                evento for evento in data["Events"] if evento["id"] != message.text
            ]
            json_update = json.dumps(data, indent=4)
            with open(
                os.path.join(os.path.dirname(__file__), "model", "Events.json"), "w"
            ) as arch:
                arch.write(json_update)

        bot.send_message(message.chat.id, "Evento eliminado")

    else:
        bot.send_message(message.chat.id, "Seleccione un número de la lista.")
        bot.register_next_step_handler(message, procesar_eliminar_evento, ids, bot)


################ info ######################
def procesar_info(message, ids, bot):
    # logica para mostrar la demas informacion del evento
    try:
        if message.text in ids:

            info = abrir_info_evento(message.text)
            bot.send_message(message.chat.id, info)
        else:
            bot.send_message(
                message.chat.id,
                "No existe ese evento, selecciona uno de los que hay en la lista",
            )
            bot.register_next_step_handler(message, procesar_info, ids, bot)

    except:
        reply_command_list(message)


############# cancelar reserva #############
def cancelar(bot, message):
    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as archivo:
        data = json.load(archivo)
        eventos_disponibles, ids = get_eventos_disponibles(data, "cancelar su recerva")
        # mostrar envetos disponibles
        if len(eventos_disponibles) != 0:
            bot.send_message(message.chat.id, eventos_disponibles)
            ### aqui lógica para cancelar recerva
        else:
            bot.send_message(message.chat.id, "No hay eventos disponibles")


############ procesasr_cerrar_evento ############
def procesar_cerrar_evento(message, ids, bot):
    if message.text in ids:
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
        ) as data:

            data = json.load(data)
            for i in data["Events"]:
                if i["id"] == message.text:
                    i["maxPlaces"] = i["current"]
                    break

        json_update = json.dumps(data, indent=4)
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"), "w"
        ) as arch:
            arch.write(json_update)
        bot.send_message(message.chat.id, "Evento cerrado")
