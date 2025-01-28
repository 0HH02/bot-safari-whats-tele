/******************************************************************/
/** index.js **/
const {
  createBot,
  createProvider,
  createFlow,
  addKeyword,
  EVENTS,
} = require("@bot-whatsapp/bot");
require("dotenv").config();

const QRPortalWeb = require("@bot-whatsapp/portal");
const BaileysProvider = require("@bot-whatsapp/provider/baileys");

// Puedes usar la base de datos que prefieras:
const MockAdapter = require("@bot-whatsapp/database/json");

// Importamos nuestros flows
const flowWelcome = require("./flows/flowWelcome");
const {
  reservar,
  nameFlow,
  tableFlow,
  confirmarFlow,
  sendInvitationFlow,
  publicidadFlow,
} = require("./flows/flowReservar");
const flowEventos = require("./flows/flowEventos");
const { codeFlow } = require("./flows/flowPromotores");
const { app } = require("./server");

// ... etc. de ser necesario

const main = async () => {
  // Adaptador de base de datos
  const adapterDB = new MockAdapter();

  // Registramos en un solo createFlow todos los flows que tenemos
  const adapterFlow = createFlow([
    flowWelcome,
    reservar,
    flowEventos,
    nameFlow,
    tableFlow,
    confirmarFlow,
    sendInvitationFlow,
    publicidadFlow,
    codeFlow,
  ]);

  // Provider para usar con Baileys (WhatsApp)
  const adapterProvider = createProvider(BaileysProvider);

  const bot = createBot({
    flow: adapterFlow,
    provider: adapterProvider,
    database: adapterDB,
  });

  QRPortalWeb();
};

main();
