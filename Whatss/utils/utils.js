const { writeFile, readFile } = require("node:fs/promises");
const { eventNames } = require("node:process");
const { createCanvas, loadImage } = require("canvas");
const fs = require("fs");
const path = require("path");
const { stat } = require("node:fs");
const { config } = require("../config/config");

const pathUsers = "./model/Users.json";
const pathEvents = "../../safari-bot/model/Events.json";

async function saveReservation(state) {
  let data = await readFile(pathEvents, "UTF-8");
  let parseData = JSON.parse(data);
  let event = parseData.Events.find((e) => e.id === state.idEvento);

  if (event) {
    const reservation = {
      CI: state.CI,
      Nombre: state.Nombre,
      Apellido_1: state.Apellido_1,
      Apellido_2: state.Apellido_2,
      Teléfono: state.Teléfono,
      ID_Evento: state.idEvento,
      confirmado: false,
      reservationId: state.reservationId,
      chat_id: "",
      table: state.table,
      partners: state.partners,
      promotorCode: state.promotorCode ? state.promotorCode : "",
    };

    if (!event.reservations) {
      event.reservations = [];
    }

    event.reservations.push(reservation);
    await state.update({ promotorCode: "" });

    await writeFile(pathEvents, JSON.stringify(parseData, null, 2), "UTF-8");
  } else {
    throw new Error("Event not found");
  }
}

async function readEvents() {
  let data = await readFile(pathEvents, "UTF-8");
  let parseData = JSON.parse(data);
  let out = "";
  parseData.Events.forEach((element) => {
    const parts = element.date.split(".");
    const d1 = new Date(
      Number(parts[2]),
      Number(parts[1]) - 1,
      Number(parts[0]) + 1
    );
    const today = new Date();
    let formattedDate = "";
    if (d1 >= today) {
      formattedDate = element.date.replaceAll(".", "-");
      out =
        out +
        `\n${element.id}     *${element.name}* \n*Fecha:* ${formattedDate} \n*Lugar:* ${element.place}\n`;
    }
  });
  return out;
}

async function getAllEvents() {
  let data = await readFile(pathEvents, "UTF-8");
  let parseData = JSON.parse(data);
  let events = [];
  parseData.Events.forEach((element) => {
    const parts = element.date.split(".");
    const d1 = new Date(
      Number(parts[2]),
      Number(parts[1]) - 1,
      Number(parts[0]) + 1
    );
    const today = new Date();
    let formattedDate = "";
    if (d1 >= today) {
      formattedDate = element.date.replaceAll(".", "\\.");
      events.push({
        id: element.id,
        name: element.name,
        date: formattedDate,
        place: element.place,
        flayers: element.flayerPhoto,
      });
    }
  });
  return events;
}

async function eventExists(id) {
  let data = await readFile(pathEvents, "UTF-8");
  let parseData = JSON.parse(data);
  let exists = false;
  parseData.Events.forEach((element) => {
    if (element.id == id) {
      exists = true;
    }
  });
  return exists;
}

async function getEvent(id) {
  let data = await readFile(pathEvents, "UTF-8");
  let parseData = JSON.parse(data);
  let event = null;
  parseData.Events.forEach((element) => {
    if (element.id == id) {
      event = element;
    }
  });
  return event;
}

async function isAgeAvilable(ci, eventNumber) {
  const event = await getEvent(eventNumber);
  const dataevento = getData(event.date);

  const anno = dataevento.getFullYear() - event.minAge;
  const datamin = new Date(anno, dataevento.getMonth(), dataevento.getDay());

  let anno2 = ci.substring(0, 2);
  if (Number.parseInt(anno2) < 60) {
    anno2 = 2000 + Number.parseInt(anno2);
  } else {
    anno2 = 1900 + Number.parseInt(anno2);
  }
  let mese = Number.parseInt(ci.substring(2, 4)) - 1;
  let gg = Number.parseInt(ci.substring(4, 6));

  const birtdate = new Date(anno2, mese, gg);
  return birtdate <= datamin;
}

function getData(dataString) {
  const parts = dataString.split(".");
  const d1 = new Date(Number(parts[2]), Number(parts[1]) - 1, Number(parts[0]));
  return d1;
}

async function saveInvitation(idEvent, text) {
  let data = await getEvent(idEvent);
  let path_to_file = path.join(__dirname, "../../safari-bot", data.photo);

  const image = await loadImage(path_to_file);
  const canvas = createCanvas(image.width, image.height);
  const context = canvas.getContext("2d"); // Dibuja la imagen en el canvas
  context.drawImage(image, 0, 0, image.width, image.height); // Configura las propiedades del texto
  context.font = "50px sans-serif"; // Cambia el tamaño y la fuente según tus necesidades
  context.fillStyle = "#000000"; // Color del texto
  const textMetrics = context.measureText(text.split(" ")[0]);
  const textWidth = textMetrics.width;
  const xPosition = (image.width - textWidth) / 2; // Dibuja el texto en el canvas
  context.fillText(text.split(" ")[0], xPosition, image.height - 480); // Guarda la imagen en el sistema de archivos
  const outputPath = path.join(
    __dirname,
    "../../safari-bot/images",
    `invitation_${idEvent}.png`
  );
  const buffer = canvas.toBuffer("image/png");
  fs.writeFileSync(outputPath, buffer);
  return `invitation_${idEvent}.png`;
}

function deleteInvitation(imagePath) {
  if (fs.existsSync(imagePath)) {
    fs.unlink(imagePath, (err) => {
      if (err) {
        console.error("Error al eliminar la imagen:", err);
        return false;
      }
      console.log("Imagen eliminada correctamente");
      return true;
    });
  } else {
    console.error("El archivo no existe en la ruta:", imagePath);
    return false;
  }
}

/**
 * Determina si el bot debe responder al mensaje recibido.
 * @param {Object} ctx - El contexto del mensaje recibido.
 * @returns {Boolean} Indica si debe responder o no.
 */
function shouldRespond(ctx, response = null) {
  if (ctx.from == config.adminPhone && ctx.body == "bot off") {
    config.botActive = false;
  }
  if (ctx.from == config.adminPhone && ctx.body == "bot on") {
    config.botActive = true;
    return false;
  }
  return config.botActive;
}

function myGotoFlow(ctx, endFlow, gotoFlow, nextFlow) {
  if (!shouldRespond(ctx)) {
    return endFlow();
  } else gotoFlow(nextFlow);
}

module.exports = {
  readEvents,
  eventExists,
  getEvent,
  isAgeAvilable,
  saveInvitation,
  deleteInvitation,
  getAllEvents,
  saveReservation,
  myGotoFlow,
  shouldRespond,
};
