import matplotlib.pyplot as plt

# Datos de los eventos proporcionados
events = [
    {
        "id": "6",
        "current": 1,
        "reservations": [
            {
                "idEvent": "6",
                "name": "Riccardo",
                "userId": "66123018588",
                "telNumber": "1234",
                "reservationId": "1",
                "confirmed": False,
            }
        ],
        "name": "😂😂 Rico",
        "date": "11.11.2023",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "maxPlaces": "3",
        "place": "Casa",
        "photo": "./images/TURQUIN2104.png",
        "minAge": "15",
        "type": "personal",
    },
    {
        "id": "6",
        "current": "0",
        "minAge": "18",
        "reservations": [],
        "name": "Fiesta Universitaria 📚",
        "date": "19.06.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "maxPlaces": "400",
        "place": "Bar Mío & Tuyo 🍸",
        "photo": "./images/TURQUIN2104.png",
        "type": "personal",
    },
    {
        "id": "7",
        "current": "0",
        "minAge": "18",
        "reservations": [],
        "name": "Viernes de Cangri 🦀",
        "date": "21.06.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "maxPlaces": "500",
        "place": "Don Cangrejo Ave 1ra y 16 Miramar",
        "photo": "./images/tarjeta_id_7.jpg",
        "type": "mesa",
    },
    {
        "id": "8",
        "current": "0",
        "minAge": "18",
        "reservations": [],
        "name": "Sábado de Turquino 🌃",
        "date": "22.06.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "maxPlaces": "250",
        "place": "Hotel Habana Libre, 25 y L Vedado",
        "photo": "./images/tarjeta_id_8.jpg",
        "type": "mesa",
        "auxMessage": "",
    },
    {
        "id": "9",
        "current": "16",
        "minAge": "18",
        "reservations": [
            # ... (reservations truncadas para brevedad)
        ],
        "name": "Hola",
        "date": "20.12.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "maxPlaces": "100",
        "auxMessage": "",
        "place": "All",
        "photo": "./images/standar_invitation.jpg",
        "flayerPhoto": [],
        "type": "personal",
    },
    {
        "id": "10",
        "current": "3",
        "minAge": "18",
        "reservations": [
            # ... (reservations truncadas para brevedad)
        ],
        "name": "Nombrecit",
        "date": "12.12.2024",
        "auxMessage": "⚠️ ¡IMPORTANTE!\n\nHorario: De 10:30pm a 4:00am\nPrecio por persona: 500 CUP \nIncluye un cóctel 🍸 de bienvenida.\n\n🔛 Su reserva será válida hasta las 12:00 am.\n\n💳 TODOS LOS PAGOS SON POR TARJETA \nLe recomendamos siempre llevar efectivo, en caso de que se vaya la conexión.\n\n💬 Si desea alguna mesa específica o VIP, contacte a nuestro comercial",
        "maxPlaces": "1000",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "place": "HL",
        "photo": "./images/standar_invitation.jpg",
        "flayerPhoto": [],
        "type": "personal",
    },
    {
        "id": "11",
        "current": "21",
        "minAge": "18",
        "reservations": [
            # ... (reservations truncadas para brevedad)
        ],
        "name": "NOmbrecitooo",
        "date": "12.12.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "auxMessage": "",
        "maxPlaces": "80",
        "place": "HB",
        "photo": "./images/standar_invitation.jpg",
        "flayerPhoto": [],
        "type": "personal",
    },
    {
        "name": "Charanga",
        "date": "07.12.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "auxMessage": "Charanganga",
        "maxPlaces": "600",
        "place": "Holguin",
        "photo": ["./images/file_6.jpg"],
        "flayerPhoto": [],
        "type": "Mesa",
        "minAge": 18,
        "current": 0,
        "id": "12",
        "reservations": [],
    },
    {
        "name": "Prueba",
        "date": "07.12.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "auxMessage": "",
        "maxPlaces": 0,
        "place": "Habana",
        "photo": [],
        "flayerPhoto": ["./images/file_9.jpg"],
        "type": "Personal",
        "minAge": 18,
        "current": 0,
        "id": "13",
        "reservations": [],
    },
    {
        "name": "Salida Guay",
        "date": "12.12.2024",
        "description": "Es un proyecto donde cantará Yomil y tendremos luces, bebidas gratis, y mucha diversión.",
        "auxMessage": "",
        "maxPlaces": "1000",
        "place": "Habana Libre",
        "photo": [],
        "flayerPhoto": ["./images/file_10.jpg"],
        "type": "Personal",
        "minAge": 18,
        "current": 0,
        "id": "14",
        "reservations": [],
    },
]

# Lista para almacenar nombres de eventos y la cantidad de asistentes
event_names = []
attendees = []

# Procesar cada evento
for event in events:
    name = event.get("name", "Sin Nombre")

    # Obtener el número actual de asistentes
    current = event.get("current", 0)

    # Asegurarse de que 'current' sea un entero
    try:
        current = int(current)
    except ValueError:
        current = 0

    # Obtener el número máximo de lugares
    max_places = event.get("maxPlaces", "500")
    try:
        max_places = int(max_places)
    except ValueError:
        max_places = 500  # Valor por defecto si falla

    # Si el número actual es 0, inventar un número aproximado
    if current == 0:
        # Asignar un número aleatorio entre 200 y max_places (o 500 si max_places es 0)
        import random

        if max_places == 0:
            current = random.randint(300, 700)
        else:
            # Asegurar que no exceda max_places
            current = random.randint(200, min(max_places, 700))

    # Agregar a las listas
    event_names.append(name)
    attendees.append(current)

# Ajustar los datos para que la cantidad total de asistentes sea aproximadamente 500 por evento
# Si hay más eventos, ajustar proporcionalmente
total_attendees = sum(attendees)
desired_total = 500 * len(attendees)

# Escalar los asistentes para que el total deseado sea alcanzado
if total_attendees != desired_total:
    scaling_factor = desired_total / total_attendees
    attendees = [int(a * scaling_factor) for a in attendees]

# Crear la gráfica de pastel
plt.figure(figsize=(10, 8))
colors = plt.cm.Paired(range(len(event_names)))  # Colores variados

# Crear la gráfica
wedges, texts, autotexts = plt.pie(
    attendees,
    labels=event_names,
    autopct="%1.1f%%",
    startangle=140,
    colors=colors,
    textprops={"fontsize": 12},
)

# Mejorar la presentación
plt.title("Distribución de Asistentes por Evento", fontsize=16)
plt.axis("equal")  # Asegura que el pastel sea circular

# Mostrar la gráfica
plt.tight_layout()
plt.show()
