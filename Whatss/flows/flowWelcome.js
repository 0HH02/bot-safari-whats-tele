/******************************************************************/
/** flows/flowWelcome.js **/
const { addKeyword, EVENTS } = require("@bot-whatsapp/bot");
const { reservar } = require("./flowReservar");
const { middleware } = require("expres");
const { config } = require("../config/config");
const { myGotoFlow, shouldRespond } = require("../utils/utils");
const idleTime = 60000 * 30;
// Podrías importar tus funciones de utils, por ejemplo:
// const { reply_command_list, find_user, ... } = require('../utils/someUtils');

module.exports = addKeyword(EVENTS.WELCOME)
  .addAction(async (ctx, { endFlow, flowDynamic }) => {
    if (ctx.from == config.adminPhone && ctx.body == "bot status") {
      await flowDynamic(`Bot ${config.botActive ? "activo" : "desactivado"}`);
      return endFlow();
    }
    if (!shouldRespond(ctx, (response = flowDynamic))) {
      return endFlow();
    }
  })
  .addAnswer(
    "¡Hola! Soy *Piñito* 🍍 reserva conmigo entradas y mesas para Safari 🌴.\n" +
      "Solo escribe el número de la opción que desees:\n\n" +
      "1 Consultar eventos 📆\n\n" +
      "2 Reservar 🎟\n\n" +
      "3 Hablar con un humano 🧑\n\n",
    { capture: true, idle: idleTime },
    async (ctx, { gotoFlow, endFlow, fallBack, flowDynamic }) => {
      const option = ctx.body.trim().toLowerCase();
      switch (option) {
        case "2":
          return myGotoFlow(ctx, endFlow, gotoFlow, reservar);
        case "1":
          return myGotoFlow(ctx, endFlow, gotoFlow, require("./flowEventos"));
        case "3":
          await flowDynamic(
            "Escriba a nuestro comercial y le atenderá con gusto:\n☎ 55395060"
          );
          return;
        default:
          await flowDynamic(
            "No entendí tu respuesta. Por favor, elige una opción válida."
          );
          if (!shouldRespond(ctx)) {
            return endFlow();
          }
          return fallBack();
      }
    }
  );
