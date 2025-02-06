/******************************************************************/
/** flows/flowReservar.js **/
const { addKeyword, EVENTS } = require("@bot-whatsapp/bot");
const {
  readEvents,
  eventExists,
  isAgeAvilable,
  getEvent,
  saveInvitation,
  deleteInvitation,
  saveReservation,
  myGotoFlow,
} = require("../utils/utils");
const { stat } = require("fs");
const { table } = require("console");
const { measureMemory } = require("vm");
const { send } = require("process");
const path = require("path");

const idleTime = 60000 * 30; //60 seg * 30

// let tempBooking = {}; // o algo así, para manejar estado
const reservar = addKeyword(EVENTS.ACTION)
  .addAction(async (ctx, { flowDynamic }) => {
    const events = await readEvents();
    await flowDynamic(events);
  })
  .addAnswer(
    "¿Cuál es el número del evento deseado:\n(Ej: 101, 102, etc.)",
    { capture: true, idle: idleTime },
    async (ctx, { flowDynamic, fallBack, gotoFlow, endFlow, state }) => {
      const idEvento = ctx.body.trim();
      await state.update({ idEvento: idEvento });
      if (!(await eventExists(idEvento))) {
        await flowDynamic(
          `El evento ${idEvento} no existe, Ingrese un número válido.\n`
        );
        return fallBack();
      } else {
        return myGotoFlow(ctx, endFlow, gotoFlow, nameFlow);
      }
    }
  );

const nameFlow = addKeyword(EVENTS.ACTION).addAnswer(
  "Escriba sus datos y de acompañantes en un único mensaje en el siguiente orden:\n\n" +
    "*Nombre Apellido1 Apellido2 Número de carnet*\n\n" +
    "\u26A0 NO admite menores de edad\n" +
    "\u26A0 NO reconoce DNI extranjeros ni pasaportes\n\n" +
    " *Ejemplo:*\n" +
    "Juan Pérez Perez 010101000\n" +
    "Ana Perez Pérez 010101000\n" +
    "Susi Perez Pérez 010101000",
  { capture: true, idle: idleTime },
  async (ctx, { flowDynamic, fallBack, state, endFlow, gotoFlow }) => {
    const lines = ctx.body.split(/\n+/).map((line) => line.trim()); // Limpiar líneas vacías y espacios
    const reservationId = (await getEvent(state.get("idEvento"))).reservations
      .length;

    const result = {
      CI: "", // Opcional si no se captura aquí
      Nombre: "",
      Apellido_1: "",
      Apellido_2: "",
      chat_id: "",
      reservationId: reservationId,
      Confirmado: false,
      partners: [],
    };

    let repeat = false;
    let currentPerson = { NombreCompleto: "", CI: "" }; // Acumula nombre y CI

    await (async () => {
      for (const line of lines) {
        if (!line) continue; // Ignorar líneas vacías

        const nameAndCIMatch = line.match(/^([A-Za-zÀ-ÿ\s-]+)\s+(\d{11})$/); // Nombre y CI en la misma línea
        const ciMatch = /^\d{11}$/.test(line); // Detectar CI
        const nameMatch = /^[A-Za-zÀ-ÿ\s-]+$/.test(line); // Detectar nombre completo
        if (nameAndCIMatch) {
          // Caso 1: Nombre completo y CI en la misma línea
          const fullName = nameAndCIMatch[1].trim();
          const ci = nameAndCIMatch[2].trim();

          const nombres = fullName.split(/\s+/);
          const Apellido_2 = nombres.pop() || ""; // Último apellido
          const Apellido_1 = nombres.pop() || ""; // Penúltimo apellido
          const Nombre = nombres.join(" ") || ""; // Lo que queda es el nombre

          if (!Nombre || !Apellido_1 || !Apellido_2 || !ci) {
            await flowDynamic(
              `Faltan datos en la entrada: "${fullName} ${ci}"`
            );
            repeat = true;
            return myGotoFlow(ctx, endFlow, gotoFlow, nameFlow);
          }

          if (!(await isAgeAvilable(ci, state.get("idEvento")))) {
            await flowDynamic(
              `La edad necesaria para entrar es de 18 años y ${Nombre} no cumple con la edad. Se ha cancelado su reserva.`
            );
            return endFlow();
          }

          if (result.Nombre === "") {
            // Si no hay titular, este es el titular
            result.Nombre = Nombre;
            result.Apellido_1 = Apellido_1;
            result.Apellido_2 = Apellido_2;
            result.CI = ci;
          } else {
            // Si ya hay titular, este es un acompañante
            result.partners.push({
              CI: ci,
              Nombre: Nombre,
              Apellido_1: Apellido_1,
              Apellido_2: Apellido_2,
            });
          }
        } else if (nameMatch) {
          // Caso 2: Solo el nombre en la línea
          currentPerson.NombreCompleto = line.trim();
        } else if (ciMatch && currentPerson.NombreCompleto) {
          // Caso 3: CI en línea separada pero el nombre ya acumulado
          currentPerson.CI = line.trim();

          const nombres = currentPerson.NombreCompleto.split(/\s+/);
          const Apellido_2 = nombres.pop() || ""; // Último apellido
          const Apellido_1 = nombres.pop() || ""; // Penúltimo apellido
          const Nombre = nombres.join(" ") || ""; // Lo que queda es el nombre

          if (!Nombre || !Apellido_1 || !Apellido_2 || !currentPerson.CI) {
            await flowDynamic(
              `Faltan datos en la entrada: "${currentPerson.NombreCompleto} ${currentPerson.CI}"`
            );
            repeat = true;
            return myGotoFlow(ctx, endFlow, gotoFlow, nameFlow);
          }

          if (!(await isAgeAvilable(currentPerson.CI, state.get("idEvento")))) {
            await flowDynamic(
              `La edad necesaria para entrar es de 18 años y ${Nombre} no cumple con la edad. Se ha cancelado su reserva.`
            );
            return endFlow();
          }

          if (result.Nombre === "") {
            // Si no hay titular, este es el titular
            result.Nombre = Nombre;
            result.Apellido_1 = Apellido_1;
            result.Apellido_2 = Apellido_2;
            result.CI = currentPerson.CI;
          } else {
            // Si ya hay titular, este es un acompañante
            result.partners.push({
              CI: currentPerson.CI,
              Nombre: Nombre,
              Apellido_1: Apellido_1,
              Apellido_2: Apellido_2,
            });
          }

          // Limpiar acumulador
          currentPerson = { NombreCompleto: "", CI: "" };
        } else {
          // Caso de error
          await flowDynamic(
            `La siguiente línea no cumple con las especificaciones:\n"${line}"`
          );
          repeat = true;
          return myGotoFlow(ctx, endFlow, gotoFlow, nameFlow);
        }
      }
    })();

    if (repeat) {
      return endFlow();
    }

    await state.update({ ...result });
    return myGotoFlow(ctx, endFlow, gotoFlow, tableFlow);
  }
);

const tableFlow = addKeyword(EVENTS.ACTION).addAnswer(
  "¿Desea una mesa? Si / No",
  { capture: true, idle: idleTime },
  async (ctx, { flowDynamic, fallBack, state, gotoFlow, endFlow }) => {
    let repeat = false;
    const table = ctx.body.trim().toLowerCase();
    if (table === "si") {
      await state.update({ table: true });
    } else if (table === "no") {
      await state.update({ table: false });
    } else {
      await flowDynamic("Por favor responda con Si o No");
      repeat = true;
      return fallBack();
    }
    if (repeat) return endFlow();
    return myGotoFlow(ctx, endFlow, gotoFlow, publicidadFlow);
  }
);

const publicidadFlow = addKeyword(EVENTS.ACTION).addAction(
  async (ctx, { state, endFlow, gotoFlow, flowDynamic }) => {
    eventObj = await getEvent(state.getMyState().idEvento);
    advertising_photo = eventObj.advertisingPhoto;
    advertising_description = eventObj.advertisingDescription;
    if (advertising_photo != "") {
      await flowDynamic(advertising_description, {
        media: `http://localhost:3050/public/${advertising_photo}`,
      });
    }

    return myGotoFlow(ctx, endFlow, gotoFlow, confirmarFlow);
  }
);

const confirmarFlow = addKeyword(EVENTS.ACTION)
  .addAction(async (ctx, { state, flowDynamic }) => {
    const data = state.getMyState();
    const message = make_reserve_string(
      data,
      await getEvent(state.get("idEvento"))
    );
    await flowDynamic(message);
    await flowDynamic("¿Desea confirmar su reserva? Si / No");
  })
  .addAnswer(
    "Estos son los datos de su reserva:",
    { capture: true, idle: idleTime },
    async (ctx, { flowDynamic, fallBack, endFlow, gotoFlow, state }) => {
      const confirm = ctx.body.trim().toLowerCase();
      if (confirm === "si") {
        console.log(state.getMyState());
        await flowDynamic("Listo! ✅");
        await flowDynamic("Enseguida le mandamos su invitación");
        saveReservation(state);
        return myGotoFlow(ctx, endFlow, gotoFlow, sendInvitationFlow);
      } else if (confirm === "no") {
        return myGotoFlow(ctx, endFlow, gotoFlow, nameFlow);
      } else {
        await flowDynamic("Por favor responda con Si o No");
        return fallBack();
      }
    }
  );

const sendInvitationFlow = addKeyword(EVENTS.ACTION).addAction(
  async (ctx, { state, flowDynamic }) => {
    
      const data = state.getMyState();
      const photoPath = await saveInvitation(
        state.get("idEvento"),
        state.get("Nombre")
      );
      await flowDynamic(
        `✅ Su reservación ha sido registrada con éxito\n\n` +
          `🎟️ *Número:* ${
            (await getEvent(data.idEvento)).reservations.length +
            50 -
            state.get("partners").length
          }\n\n` +
          `\u26A0 Conserve este mensaje para mostrarlo a la entrada.\n\n` +
          `💬 Ante cualquier necesidad contacte a nuestro comercial.\n*Nacho* +53 56511592\n\n` +
          `¡Comparte tu boleto y etiquétanos!\n\n` +
          `\u2764 *Instagram* @safari.havana\n` +
          `https://www.instagram.com/safari.havana?igsh=MTlkYTNiaXN4dDdvZg%3D%3D&utm_source=qr`,
        {
          media: `http://localhost:3050/public/images/${photoPath}`,
        }
      );

      deleteInvitation(
        path.join(__dirname, "../../safari-bot/images/", photoPath)
      );
      let index = 1;
      await (async () => {
        for (const partner of state.get("partners")) {
          const photoPath = await saveInvitation(
            state.get("idEvento"),
            partner["Nombre"]
          );
          await flowDynamic(
            `✅ Su reservación ha sido registrada con éxito\n\n` +
              `🎟️ *Número:* ${
                (await getEvent(data.idEvento)).reservations.length +
                50 -
                state.get("partners").length +
                index
              }\n\n` +
              `\u26A0 Conserve este mensaje para mostrarlo a la entrada.\n\n` +
              `💬 Ante cualquier necesidad contacte a nuestro comercial.\n*Nacho* +53 56511592\n\n` +
              `¡Comparte tu boleto y etiquétanos!\n\n` +
              `\u2764 *Instagram* @safari.havana\n` +
              `https://www.instagram.com/safari.havana?igsh=MTlkYTNiaXN4dDdvZg%3D%3D&utm_source=qr`,
            {
              media: `http://localhost:3050/public/images/${photoPath}`,
            }
          );
          deleteInvitation(
            path.join(__dirname, "../../safari-bot/images/", photoPath)
          );
          index += 1;
        }
      })();
  }
);

function make_reserve_string(reservation_data, event_data) {
  let message = `🔷 *Verifique sus datos por favor*\n\n`;
  message += `*Evento:* ${event_data["name"]}\n`;
  message += `*Fecha:* ${event_data["date"]}\n`;
  message += `*Ubicación:* ${event_data["place"]}\n`;
  message += `*Mesa:* ${reservation_data["table"] ? "Si" : "No"}\n\n`;

  message += `👤 *A nombre de: ${reservation_data["Nombre"]} ${reservation_data["Apellido_1"]} ${reservation_data["Apellido_2"]} ${reservation_data["CI"]}*\n\n`;

  for (partner of reservation_data["partners"]) {
    message += `${partner["Nombre"]} ${partner["Apellido_1"]} ${partner["Apellido_2"]} ${partner["CI"]}\n`;
  }
  return message;
}

module.exports = {
  reservar,
  nameFlow,
  tableFlow,
  confirmarFlow,
  sendInvitationFlow,
  publicidadFlow,
};
