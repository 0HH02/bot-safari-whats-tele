const express = require("express");
const app = express();
const path = require("path");

// Configura la carpeta pública
app.use("/public", express.static(path.join(__dirname, "../safari-bot/")));

// Inicia el servidor
app.listen(3051, () => {
  console.log("Servidor corriendo en http://localhost:3050");
});
