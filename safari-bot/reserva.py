import re
from datetime import datetime
import os
import json
from utils import buscar_indice_evento, get_eventos_disponibles
import cv2
import telebot
from ai import ask_to_ai, semantic_correction
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_id_reservation(data):
    if len(data) == 0:
        return 0
    ultimo = data[-1]["reservationId"]
    return ultimo


def guardar(index, invitados, partners, chat_id):
    with open(os.path.join("model", "Users.json"), "r", encoding="utf-8") as users:
        users_data = json.load(users)

        if str(chat_id) in list(users_data["Users"].keys()):
            users_data["Users"][str(chat_id)]["ID_Evento"] = invitados["ID_Evento"]
            users_data["Users"][str(chat_id)]["FechaUltimoEvento"] = str(
                datetime.now()
            ).split()[0]
            users_data["Users"][str(chat_id)]["Amigos"] = [
                partner["Nombre"] for partner in partners
            ]
        else:
            users_data["Users"][chat_id] = invitados
            users_data["Users"][chat_id]["FechaUltimoEvento"] = str(
                datetime.now()
            ).split()[0]
            users_data["Users"][chat_id]["Amigos"] = [
                partner["Nombre"] for partner in partners
            ]

    with open(
        os.path.join("model", "Events.json"),
        "r",
        encoding="utf-8",
    ) as archivo:
        events = json.load(archivo)
        events["Events"][index]["current"] = str(
            int(events["Events"][index]["current"]) + 1
        )
        users_data["Users"][str(chat_id)]["LugarUltimoEvento"] = events["Events"][
            index
        ]["place"]
    with open(os.path.join("model", "Users.json"), "w") as user1:
        json.dump(users_data, user1, indent=4)

        invitados["partners"] = partners
        events["Events"][index]["reservations"].append(invitados)
    with open(os.path.join("model", "Events.json"), "w") as arc:
        json.dump(events, arc, indent=4)


def sms_end(bot, message, ultimo_id_reservation):
    bot.send_message(
        message.chat.id,
        f"""Su reservación ha sido registrada con éxito. ✅
Número de reserva: {int(ultimo_id_reservation)+1}

Conserve este mensaje como comprobante. 🧾 El pago se realiza en puerta el día del evento.

Ante cualquier necesidad, contacte a nuestro\n comercial:

☎ Peter 55395060

✨ ¡Comparte tu Boleto Digital y etiquétanos en Instagram! @safari.havana""",
    )


def make_dict_personal_reservation(
    ci, name, apellido1, apellido2, phone_number, id, index, data
):
    invitados = {}
    invitados["CI"] = ci
    invitados["Nombre"] = name
    invitados["Apellido_1"] = apellido1
    invitados["Apellido_2"] = apellido2
    invitados["Teléfono"] = phone_number
    invitados["ID_Evento"] = id
    invitados["Confirmado"] = False
    invitados["reservationId"] = str(
        int(get_id_reservation(data["Events"][index]["reservations"])) + 1
    )
    return invitados


def make_img(name):
    img = cv2.imread(
        os.path.join(os.path.dirname(__file__), "images", "standar_invitation.jpg")
    )
    font = cv2.FONT_HERSHEY_SIMPLEX
    tamañoLetra = 2
    colorLetra = (0, 0, 0)  # color negro
    grosorLetra = 3
    a, b, _ = img.shape

    cv2.putText(
        img,
        f"{name}",
        (int((a // 2) - 340), int((b // 2) + 280)),
        font,
        tamañoLetra,
        colorLetra,
        grosorLetra,
    )
    return img


def confirm_reservation(
    message: telebot.types.Message,
    bot: telebot.TeleBot,
    invitados: str,
    index: int,
    ultimo_id_reservation: int,
    img: str,
    ci: str,
    partners: list,
):
    if message.text.lower() == "confirmar":
        sms_end(bot, message, ultimo_id_reservation)
        cv2.imwrite("images/imagen_modificada.jpg", img)
        with open("images/imagen_modificada.jpg", "rb") as foto:
            bot.send_photo(message.chat.id, foto)
            guardar(index, invitados, partners, message.chat.id)  # guardar los datos
    elif message.text.lower() == "cancelar":
        bot.send_message(message.chat.id, "No se ha registrado la reserva")
    else:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("Cancelar"), KeyboardButton("Confirmar"))
        bot.send_message(
            message.chat.id,
            "¿Desea confirmar o editar la reserva?",
            reply_markup=markup,
        )
        bot.register_next_step_handler(
            message,
            confirm_reservation,
            bot,
            invitados,
            index,
            ultimo_id_reservation,
            img,
            ci,
            partners,
        )


def aux_end(
    message: telebot.types.Message,
    bot: telebot.TeleBot,
    ci: str,
    full_name: str,
    phone_number: str,
    id: str,
):

    with open(
        os.path.join(os.path.dirname(__file__), "model", "Events.json"), "r"
    ) as file:
        data = json.load(file)

    index = buscar_indice_evento(data, id)
    clean_name = ask_to_ai(
        f"Devuelve una lista donde venga el nombre de pila, el primer apellido y el segundo apellido: {full_name}",
        "Ejemplo: Alejandro Manuel Coin Toprá\nTu respuesta: ['Alejandro', 'Coin', 'Toprá']",
        "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
    )
    list_name = eval(clean_name)
    name = list_name[0]
    apellido1 = list_name[1]
    apellido2 = list_name[2]

    invitados = make_dict_personal_reservation(
        ci, name, apellido1, apellido2, phone_number, id, index, data
    )
    invitados["chat_id"] = message.chat.id
    img = make_img(name)
    ultimo_id_reservation = get_id_reservation(data["Events"][index]["reservations"])

    if message.text.lower() == "no":
        current = data["Events"][index]["current"]
        maxPlaces = data["Events"][index]["maxPlaces"]

        ## hacer el flayer
        if current == maxPlaces:
            bot.send_message(
                message.chat.id,
                "Este evento está lleno, puede selecionar otro de la lista",
            )
            disponibles, ids = get_eventos_disponibles(data, "reservar")
            if len(disponibles) != 0:
                bot.send_message(message.chat.id, disponibles)
                bot.register_next_step_handler(message, procesar_reserva, ids, bot)
            else:
                bot.send_message(message.chat.id, "No hay evnetos disponibles")

        else:
            bot.send_message(
                message.chat.id,
                f"Estos son los datos de su reserva:\n"
                f"Nombre del Evento: {data['Events'][index]['name']}\n"
                f"Fecha: {data['Events'][index]['date']}\n"
                f"Lugar: {data['Events'][index]['place']}\n\n"
                f"Nombre: {invitados['Nombre']} {invitados['Apellido_1']} {invitados['Apellido_2']}\n"
                f"CI: {invitados['CI']}\n"
                f"Teléfono: {invitados['Teléfono']}",
            )
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(KeyboardButton("Editar"), KeyboardButton("Confirmar"))
            bot.send_message(
                message.chat.id,
                "¿Desea confirmar o editar la reserva?",
                reply_markup=markup,
            )
            bot.register_next_step_handler(
                message,
                confirm_reservation,
                bot,
                invitados,
                index,
                ultimo_id_reservation,
                img,
                ci,
                [],
            )

    else:
        invitados["table"] = []
        bot.send_message(
            message.chat.id,
            "¿Cuántas personas van con usted? Máximo 11.",
        )
        bot.register_next_step_handler(
            message,
            more_invitados,
            id,
            bot,
            ci,
            index,
            ultimo_id_reservation,
            img,
            invitados,
            data,
        )


def more_invitados(
    message: telebot.types.Message,
    id: str,
    bot: telebot.TeleBot,
    ci: str,
    index: int,
    ultimo_id_reservation: int,
    img,
    invitados,
    data,
):
    try:
        if 1 <= int(message.text) <= 11:
            bot.send_message(
                message.chat.id,
                "Introduzca el nombre, los dos apellidos, el carnet de identidad y el teléfono de su primer acompañante. (Todo en un mismo mensaje separado por comas).\nEjemplo:\n Alejandro Manuel Coin Toprá, 99031279327, 54252449",
            )
            bot.register_next_step_handler(
                message,
                comprobar_data_recerva_aux,
                bot,
                ci,
                1,
                int(message.text),
                index,
                ultimo_id_reservation,
                img,
                [],
                invitados,
                data,
                id,
            )

        else:
            bot.send_message(
                message.chat.id,
                "La cantidad de personas que van con usted debe ser un número del 1 al 11",
            )
            bot.register_next_step_handler(
                message,
                more_invitados,
                id,
                bot,
                ci,
                index,
                ultimo_id_reservation,
                img,
                data,
            )

    except:
        bot.send_message(
            message.chat.id,
            "La cantidad de personas que van con usted debe ser un número del 1 al 11",
        )
        bot.register_next_step_handler(
            message,
            more_invitados,
            id,
            bot,
            ci,
            index,
            ultimo_id_reservation,
            img,
            data,
        )


def add_partner(bot, message, id, index, data_event):
    try:
        data: list[str] = message.text.split(", ")
        if len(data) == 3:
            full_name, ci, phone_number = data[0], data[1], data[2]
            if (
                check_name(full_name, bot, message)
                and check_ci(ci, bot, message)
                and check_phone(phone_number, bot, message)
            ):
                if check_age(ci, bot, message):
                    clean_name = ask_to_ai(
                        f"Devuelve una lista donde venga el nombre de pila, el primer apellido y el segundo apellido: {full_name}",
                        "Ejemplo: Alejandro Manuel Coin Toprá\nTu respuesta: ['Alejandro', 'Coin', 'Toprá']",
                        "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
                    )
                    list_name = eval(clean_name)
                    name = list_name[0]
                    apellido1 = list_name[1]
                    apellido2 = list_name[2]
                    partner = make_dict_personal_reservation(
                        ci,
                        name,
                        apellido1,
                        apellido2,
                        phone_number,
                        id,
                        index,
                        data_event,
                    )
                    print(partner)
                    return partner
            else:
                bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)
        else:
            message_error = ask_to_ai(
                semantic_correction(
                    "Nombre: Alejandro Manuel Coin Toprá, CI: 99031279327, Teléfono: 54252449",
                    message.text,
                ),
                "",
                "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
            )
            bot.send_message(
                message.chat.id,
                message_error,
            )
            bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Su mensaje debe cumplir las normas establecidas. Vuelva a intentarlo. {str(e)}",
        )
        bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)


def make_reserve_string(partners, invitados, data, index, ci):
    message = f"Estos son los datos de su reserva:\n"
    message += f"Nombre del Evento: {data['Events'][index]['name']}\n"
    message += f"Fecha: {data['Events'][index]['date']}\n"
    message += f"Lugar: {data['Events'][index]['place']}\n\n"
    message += f"Nombre: {invitados['Nombre']} {invitados['Apellido_1']} {invitados['Apellido_2']}\n"
    message += f"CI: {invitados['CI']}\n"
    message += f"Teléfono: {invitados['Teléfono']}\n"

    if len(partners) >= 1:
        message += f"\nAcompañantes:\n"
    for partner in partners:
        message += f"Nombre: {partner['Nombre']} {partner['Apellido_1']} {partner['Apellido_2']}\n"
        message += f"CI: {partner['CI']}\n"
        message += f"Teléfono: {partner['Teléfono']}\n"
    return message


def comprobar_data_recerva_aux(
    message: telebot.types.Message,
    bot: telebot.TeleBot,
    ci,
    contador,
    maximo,
    index,
    ultimo_id_reservation,
    img,
    partners: list,
    invitados,
    data,
    id,
):
    if contador < maximo:
        partners.append(add_partner(bot, message, id, index, data))
        contador += 1
        bot.send_message(
            message.chat.id,
            f"Introduzca el nombre, los dos apellidos, el carnet de identidad y el teléfono de su acompañante número {contador}. (Todo en un mismo mensaje separado por comas).\nEjemplo:\n Alejandro Manuel Coin Toprá, 99031279327, 54252449",
        )
        bot.register_next_step_handler(
            message,
            comprobar_data_recerva_aux,
            bot,
            ci,
            contador,
            maximo,
            index,
            ultimo_id_reservation,
            img,
            partners,
            invitados,
            data,
            id,
        )
    else:
        partners.append(add_partner(bot, message, id, index, data))
        message_reserve = make_reserve_string(
            partners, invitados, data, index, ci
        )
        bot.send_message(message.chat.id, message_reserve)

        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton("Editar"), KeyboardButton("Confirmar"))
        bot.send_message(
            message.chat.id,
            "¿Desea confirmar o editar la reserva?",
            reply_markup=markup,
        )
        bot.register_next_step_handler(
            message,
            confirm_reservation,
            bot,
            invitados,
            index,
            ultimo_id_reservation,
            img,
            ci,
            partners,
        )


def table_reserve(
    message: telebot.types.Message,
    ci: str,
    full_name: str,
    phone_number: str,
    bot: telebot.TeleBot,
    id: str,
):
    if message.text.lower() == "si":
        aux_end(message, bot, ci, full_name, phone_number, id)
    elif message.text.lower() == "no":
        aux_end(message, bot, ci, full_name, phone_number, id)
    else:
        message_error = ask_to_ai(
            semantic_correction(
                "Respuesta a: ¿Desea reservar una mesa? (Responda: Si/No)",
                message.text,
            ),
            "",
            "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
        )
        bot.send_message(
            message.chat.id,
            message_error,
        )
        bot.register_next_step_handler(
            message, table_reserve, ci, full_name, phone_number, bot, id
        )


def check_name(full_name, bot: telebot.TeleBot, message: telebot.types.Message):
    if len(full_name.split()) >= 3:
        return True
    else:
        message_error = ask_to_ai(
            semantic_correction(
                "Nombre y dos apellidos: Alejandro Manuel Coin Toprá",
                full_name,
            ),
            "",
            "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
        )
        bot.send_message(
            message.chat.id,
            message_error,
        )
        return False


def check_ci(ci, bot: telebot.TeleBot, message: telebot.types.Message):
    if re.match(r"^\d{11}$", ci):
        return True
    else:
        bot.send_message(
            message.chat.id,
            "Su Carnet de Identidad debe tener 11 números. Vuelva a intentar escribir todos sus datos como lo muestra el ejemplo:\nAlejandro Manuel Coin Toprá, 99031279327, 54252449",
        )
        return False


def check_age(ci, bot: telebot.TeleBot, message: telebot.types.Message):
    fecha = ci[:6]
    hoy = datetime.today()
    fecha_objeto = datetime.strptime(fecha, "%y%m%d")
    edad = (
        hoy.year
        - fecha_objeto.year
        - ((hoy.month, hoy.day) < (fecha_objeto.month, fecha_objeto.day))
    )
    if int(edad) >= 18:
        return True
    else:
        bot.send_message(
            message.chat.id,
            "Necesitas tener al menos 18 años para reservar😕. La reserva ha sido cancelada.",
        )
        bot.send_message(
            message.chat.id,
            "Puede seguir viendo las ofertas de eventos en la lista. Puede que tengamos algún evento para todas las edades😊",
        )
        return False


def check_phone(phone_number, bot: telebot.TeleBot, message: telebot.types.Message):
    if re.match(r"^\d{8}$", phone_number):
        return True
    else:
        bot.send_message(
            message.chat.id,
            "El número de teléfono debe tener 8 números. Vuelva a intentar escribir todos sus datos como lo muestra el ejemplo:\nAlejandro Manuel Coin Toprá, 99031279327, 54252449",
        )
        return False


def procesar_datos_reserva(message: telebot.types.Message, bot: telebot.TeleBot, id):
    try:
        data: list[str] = message.text.split(", ")
        if len(data) == 3:
            full_name, ci, phone_number = data[0], data[1], data[2]
            if (
                check_name(full_name, bot, message)
                and check_ci(ci, bot, message)
                and check_phone(phone_number, bot, message)
            ):
                if check_age(ci, bot, message):
                    markup = ReplyKeyboardMarkup(
                        one_time_keyboard=True, resize_keyboard=True
                    )
                    markup.add(KeyboardButton("Si"), KeyboardButton("No"))
                    bot.send_message(
                        message.chat.id,
                        "¿Desea reservar una mesa? (Responda: Si/No)",
                        reply_markup=markup,
                    )
                    bot.register_next_step_handler(
                        message, table_reserve, ci, full_name, phone_number, bot, id
                    )
            else:
                bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)
        else:
            message_error = ask_to_ai(
                semantic_correction(
                    "Nombre: Alejandro Manuel Coin Toprá, CI: 99031279327, Teléfono: 54252449",
                    message.text,
                ),
                "",
                "Eres un asistente virtual amable y educado ayudando a un cliente a completar una reserva.",
            )
            bot.send_message(
                message.chat.id,
                message_error,
            )
            bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)
    except:
        bot.send_message(
            message.chat.id,
            "Su mensaje debe cumplir las normas establecidas. Vuelva a intentarlo.",
        )
        bot.register_next_step_handler(message, procesar_datos_reserva, bot, id)


def procesar_reserva(message: telebot.types.Message, ids, bot: telebot.TeleBot):
    try:
        if message.text in ids:
            ## aqui falta comprobar primero si está lleno el evento y sugerirle otro antes de pedir los datos
            # lógica para pedir los datos para la recerva,
            # si ya tiene número de promotor con solo ponerlo y sea válido tiene
            bot.send_message(
                message.chat.id,
                "Introduzca su nombre, dos apellidos, carnet de identidad y teléfono. (Todo en un mismo mensaje separado por comas).\nEjemplo:\n Alejandro Manuel Coin Toprá, 99031279327, 54252449",
            )
            bot.register_next_step_handler(
                message, procesar_datos_reserva, bot, message.text
            )
        else:
            bot.send_message(
                message.chat.id, "Escriba un número de la lista para reservar"
            )
            bot.register_next_step_handler(message, procesar_reserva, ids, bot)
    except:
        bot.send_message(message.chat.id, "Escriba un número de la lista para reservar")
        bot.register_next_step_handler(message, procesar_reserva, ids, bot)
