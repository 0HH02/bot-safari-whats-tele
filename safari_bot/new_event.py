import os
import json
import re
from datetime import datetime
from utils import get_ultimo_id

eventos = {}  # para agregar el nuevo evrnto


foto = (
    {}
)  # para agregar los flayer personalizados, cuando se está agregando el nuevo eveto


def save_image(message, nombre_evento, bot):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(f'images/{file_info.file_path.split("/")[-1]}', "wb") as new_file:
        new_file.write(downloaded_file)
        eventos[nombre_evento]["photo"] = f'images/{file_info.file_path.split("/")[-1]}'
    
        


def procesar_nombre_evento(message, bot):
    if message.content_type == "photo":
        bot.send_message(message.chat.id, "El nombre del evento no puede ser una foto")
        bot.send_message(message.chat.id, "¿Cuál es el nombre del evento?")
        bot.register_next_step_handler(message, procesar_nombre_evento, bot)
    else:
        nombre_evento = message.text
        eventos[nombre_evento] = {"name": nombre_evento}

        bot.send_message(
            message.chat.id, "¿Cuál es la fecha del evento? (Formato: DD.MM.AAAA)"
        )
        bot.register_next_step_handler(
            message, procesar_fecha_evento, nombre_evento, bot
        )


def procesar_fecha_evento(message, nombre_evento, bot):
    if message.content_type == "photo":
        bot.send_message(message.chat.id, "La fecha del evento no puede ser una foto")
        bot.send_message(
            message.chat.id, "¿Cuál es la fecha del evento? (Formato: DD.MM.AAAA)"
        )
        bot.register_next_step_handler(
            message, procesar_fecha_evento, nombre_evento, bot
        )
    else:
        fecha_evento = message.text
        # Validar el formato de la fecha
        if re.match(r"^\d{2}\.\d{2}\.\d{4}$", fecha_evento):
            try:
                # Intentar convertir la fecha a un objeto datetime para validar su existencia
                fecha_valida = datetime.strptime(fecha_evento, "%d.%m.%Y")
                eventos[nombre_evento]["date"] = fecha_evento

                bot.send_message(
                    message.chat.id,
                    "Describe el evento",
                )
                bot.register_next_step_handler(
                    message, procesar_descripcion_evento, nombre_evento, bot
                )

            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "La fecha debe estar en formato DD.MM.AA. Por favor, inténtalo de nuevo.",
                )

                # repetir función
                message = bot.register_next_step_handler(
                    message, procesar_fecha_evento, nombre_evento, bot
                )
        else:
            bot.send_message(
                message.chat.id,
                "La fecha debe estar en formato DD.MM.AA. Por favor, inténtalo de nuevo.",
            )

            # repetir función
            message = bot.register_next_step_handler(
                message, procesar_fecha_evento, nombre_evento, bot
            )


def procesar_descripcion_evento(message, nombre_evento, bot):
    descripcion = message.text
    eventos[nombre_evento]["description"] = descripcion
    bot.send_message(
        message.chat.id, "¿Texto auxiliar? (Escribe 'no' si no hay texto auxiliar)"
    )
    bot.register_next_step_handler(message, procesar_texto_auxiliar, nombre_evento, bot)


def procesar_texto_auxiliar(message, nombre_evento, bot):
    if message.content_type == "photo":
        bot.send_message(message.chat.id, "El texto auxiliar no puede ser una foto")
        bot.send_message(
            message.chat.id,
            "¿Cuál es el texto auxiliar?(Escribe 'no' si no hay texto auxiliar) ",
        )
        bot.register_next_step_handler(
            message, procesar_texto_auxiliar, nombre_evento, bot
        )
    else:
        texto_auxiliar = message.text
        eventos[nombre_evento]["auxMessage"] = (
            texto_auxiliar if texto_auxiliar.lower() != "no" else ""
        )
        bot.send_message(message.chat.id, "¿Número máximo de plazas?")
        bot.register_next_step_handler(message, procesar_max_plazas, nombre_evento, bot)


def procesar_max_plazas(message, nombre_evento, bot):
    if message.content_type == "photo":
        bot.send_message(
            message.chat.id, "El número máximo de plazas no puede ser una foto"
        )
        bot.send_message(message.chat.id, "¿Cuál es el número máximo de plazas?")
        bot.register_next_step_handler(message, procesar_max_plazas, nombre_evento, bot)
    else:
        max_plazas = message.text
        if max_plazas.isdigit():

            if int(max_plazas) > 0:
                eventos[nombre_evento]["maxPlaces"] = max_plazas
                bot.send_message(message.chat.id, "¿Lugar?")
                bot.register_next_step_handler(
                    message, procesar_lugar, nombre_evento, bot
                )
            else:
                bot.send_message(
                    message.chat.id, "El número minímo de plazas debe ser mayor que 0"
                )
                bot.register_next_step_handler(
                    message, procesar_max_plazas, nombre_evento, bot
                )

        else:
            bot.send_message(message.chat.id, "el número de plazas debe ser un número.")
            bot.register_next_step_handler(
                message, procesar_max_plazas, nombre_evento, bot
            )


def procesar_lugar(message, nombre_evento, bot):
    if message.content_type == "photo":
        bot.send_message(message.chat.id, "El lugar no puede ser una foto")
        bot.send_message(message.chat.id, "¿Cuál es el lugar?")
        bot.register_next_step_handler(message, procesar_lugar, nombre_evento, bot)
    else:
        lugar = message.text
        eventos[nombre_evento]["place"] = lugar
        bot.send_message(
            message.chat.id,
            "'Tiene foto de invitación personalizada?\n(Si tiene foto, súbala directamente, de lo contrario diga que no)'",
        )
        foto[message.chat.id] = True
        try:
            bot.register_next_step_handler(message, procesar_foto, nombre_evento, bot)
        except:
            print("No se pudo procesar la foto")


def procesar_foto(message, nombre_evento, bot):
    if message.content_type == "photo":
        # guardar foto y actualizar el diccionario eventos con el url
        eventos[nombre_evento]["photo"] = ""
        save_image(message, nombre_evento, bot)
    elif message.text.lower() == "no":
        eventos[nombre_evento]["photo"] = "images/standar_invitation.jpg"
        bot.send_message(message.chat.id, "Envía el flayer del evento")
        bot.register_next_step_handler(message, procesar_flayer, nombre_evento, bot)
    else:
        bot.send_message(message.chat.id, "Escribe 'no' o envie la foto.")
        bot.register_next_step_handler(message, procesar_foto, nombre_evento, bot)


def procesar_flayer(message, nombre_evento, bot):
    if message.content_type == "photo":
        # guardar foto y actualizar el diccionario eventos con el url
        eventos[nombre_evento]["flayerPhoto"] = []

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(f'images/{file_info.file_path.split("/")[-1]}', "wb") as new_file:
            new_file.write(downloaded_file)
            eventos[nombre_evento]["flayerPhoto"].append(
                f'images/{file_info.file_path.split("/")[-1]}'
            )
        bot.send_message(message.chat.id, "Si tiene publicidad envía la foto con la descripción, de lo contrario escriba: no")
        bot.register_next_step_handler(
            message, procesar_publicidad, nombre_evento, bot
        )
    else:
        bot.send_message(
            message.chat.id,
            "A ocurrido algún error al recibir la foto, envíe nuevamente el flayer del evento.",
        )
        bot.register_next_step_handler(message, procesar_flayer, nombre_evento, bot)


def pedir_mas_fotos(message, nombre_evento, bot):
    try:
        if message.content_type == "photo":
            # guardar foto
            save_image(message, nombre_evento, bot)
            bot.send_message(
                message.chat.id,
                "Foto recibida. Puedes enviar más fotos o escribir 'ya' para finalizar.",
            )
            bot.register_next_step_handler(message, pedir_mas_fotos, nombre_evento, bot)

        elif message.text.lower() == "ya":
            bot.send_message(message.chat.id, "Envía el flayer del evento")
            bot.register_next_step_handler(message, procesar_flayer, nombre_evento, bot)
    except:
        bot.send_message(message.chat.id, "Asegúrate de enviar una foto válida")
        bot.register_next_step_handler(message, pedir_mas_fotos, nombre_evento, bot)


def procesar_publicidad(message, nombre_evento, bot):
    try:
        if message.content_type == "photo":
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(f'images/{nombre_evento}_{file_info.file_path.split("/")[-1]}', "wb") as new_file:
                new_file.write(downloaded_file)
                eventos[nombre_evento]["advertisingPhoto"] = f'images/{nombre_evento}_{file_info.file_path.split("/")[-1]}'
            description = ""
            if message.caption:  # message.caption contiene el texto adjunto a la foto
                description = message.caption
            eventos[nombre_evento]["advertisingDescription"] = description

            bot.send_message(message.chat.id, "Tipo Evento (personal/mesa)")
            bot.register_next_step_handler(
                message, procesar_tipo_evento, nombre_evento, bot
            )
        elif message.text.lower() == "no":
            eventos[nombre_evento]["advertisingPhoto"] = ""
            eventos[nombre_evento]["advertisingDescription"] = ""
            bot.send_message(message.chat.id, "Tipo Evento (personal/mesa)")
            bot.register_next_step_handler(
                message, procesar_tipo_evento, nombre_evento, bot
            )
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Asegúrate de enviar una respuesta válida")
        bot.register_next_step_handler(message, procesar_publicidad, nombre_evento, bot)
    

def procesar_tipo_evento(message, nombre_evento, bot):
    tipo_evento = message.text

    if tipo_evento.lower() in ["personal", "mesa"]:
        eventos[nombre_evento]["type"] = tipo_evento
        eventos[nombre_evento]["minAge"] = 18
        eventos[nombre_evento]["current"] = 0
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"),
            "r",
            encoding="utf-8",
        ) as date:
            data = json.load(date)
            eventos[nombre_evento]["id"] = str(get_ultimo_id(data) + 1)
            eventos[nombre_evento]["reservations"] = []
        # Aquí ya guardar toda la información de la variable evento en el JSON
        # falta agregarle los id al diccionnario eventos
        # revisar las demas cosas que hay que agregar al evento, estan en el archivo json
        data["Events"].append(eventos[nombre_evento])

        # Escribir los datos actualizados de nuevo en el archivo JSON
        with open(
            os.path.join(os.path.dirname(__file__), "model", "Events.json"), "w"
        ) as archivo:
            json.dump(data, archivo, indent=4)

        bot.send_message(message.chat.id, "evento registrado correctamente.")

    else:
        bot.send_message(
            message.chat.id,
            "El evento tiene que ser 'personal' o 'mesa'. Por favor, inténtalo de nuevo.",
        )
        # Volver a registrar el siguiente paso para repetir la pregunta
        bot.register_next_step_handler(
            message, procesar_tipo_evento, nombre_evento, bot
        )
