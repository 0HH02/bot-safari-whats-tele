/******************************************************************/
/** flows/flowPromotores.js **/
const { addKeyword, EVENTS } = require("@bot-whatsapp/bot");
const { reservar } = require("./flowReservar");
const { myGotoFlow } = require("../utils/utils");
const idleTime = 60000 * 30;

function checkCode(ctx) {
  return ctx.body.toLowerCase() == "1234";
}

const codeFlow = addKeyword("promotor").addAnswer(
  "Escriba su código de promotor",
  { capture: true, idle: idleTime },
  async (ctx, { state, endFlow, flowDynamic, gotoFlow }) => {
    if (checkCode(ctx)) {
      await state.update({ promotorCode: ctx.body });
      await myGotoFlow(ctx, endFlow, gotoFlow, reservar);
    } else {
      await flowDynamic("Código de promotor incorrecto");
      return endFlow();
    }
  }
);
module.exports = {
  codeFlow,
};
