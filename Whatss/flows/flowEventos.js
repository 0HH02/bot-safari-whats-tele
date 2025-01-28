/******************************************************************/
/** flows/flowEventos.js **/

const { addKeyword, EVENTS } = require("@bot-whatsapp/bot");
const { getAllEvents, myGotoFlow } = require("../utils/utils");
const { reservar } = require("./flowReservar");
const idleTime = 60000 * 30; // 60 seg * 30

module.exports = addKeyword(EVENTS.ACTION)
  .addAction(async (ctx, { flowDynamic }) => {
    const events = await getAllEvents();
    await (async () => {
      for (const evento of events) {
        await flowDynamic(
          `\n${evento.id}     *${evento.name}* \n*Fecha:* _${evento.date}_ \n*Lugar:* ${evento.place}\n`,
          { media: `http://localhost:3050/public/${evento.flayers[0]}` }
        );
      }
    })();
    await flowDynamic("¿Desea reservar para alguno de estos eventos? Si / No");
  })
  .addAnswer(
    "Estos son nuestros próximos eventos:\n",
    { capture: true, idle: idleTime },
    async (ctx, { state, flowDynamic, endflow, gotoFlow, fallBack }) => {
      const confirm = ctx.body.trim().toLowerCase();
      if (confirm === "si") {
        return myGotoFlow(ctx, endflow, gotoFlow, reservar);
      } else {
        await flowDynamic(
          "¡Manténgase al tanto de nuestros próximos eventos! 😊"
        );
      }
    }
  );
