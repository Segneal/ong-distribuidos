#!/bin/bash
# Add messaging routes to server.js
sed -i '/const eventsRoutes = require/a const messagingRoutes = require("./routes/messaging-fixed");' /app/src/server.js
sed -i '/app.use.*events.*eventsRoutes/a app.use("/api/messaging", messagingRoutes);' /app/src/server.js
# Restart the server
pkill -f "node src/server.js"
node src/server.js