const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Configuración de proto loader
const protoOptions = {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
};

// URLs de los microservicios
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'localhost:50051';
const INVENTORY_SERVICE_URL = process.env.INVENTORY_SERVICE_URL || 'localhost:50052';
const EVENTS_SERVICE_URL = process.env.EVENTS_SERVICE_URL || 'localhost:50053';

// Cargar archivos proto
const userProtoPath = path.join(__dirname, '../../proto/users.proto');
const inventoryProtoPath = path.join(__dirname, '../../proto/inventory.proto');
const eventsProtoPath = path.join(__dirname, '../../proto/events.proto');

// Cargar definiciones proto
const userPackageDefinition = protoLoader.loadSync(userProtoPath, protoOptions);
const inventoryPackageDefinition = protoLoader.loadSync(inventoryProtoPath, protoOptions);
const eventsPackageDefinition = protoLoader.loadSync(eventsProtoPath, protoOptions);

// Crear objetos gRPC
const userProto = grpc.loadPackageDefinition(userPackageDefinition).users;
const inventoryProto = grpc.loadPackageDefinition(inventoryPackageDefinition).inventory;
const eventsProto = grpc.loadPackageDefinition(eventsPackageDefinition).events;

// Crear clientes gRPC
const userClient = new userProto.UserService(
  USER_SERVICE_URL,
  grpc.credentials.createInsecure()
);

const inventoryClient = new inventoryProto.InventoryService(
  INVENTORY_SERVICE_URL,
  grpc.credentials.createInsecure()
);

const eventsClient = new eventsProto.EventsService(
  EVENTS_SERVICE_URL,
  grpc.credentials.createInsecure()
);

// Función helper para promisificar llamadas gRPC
const promisifyGrpcCall = (client, method) => {
  return (request) => {
    return new Promise((resolve, reject) => {
      console.log(`GRPC CLIENT: Calling ${method} with request:`, JSON.stringify(request, null, 2));
      client[method](request, (error, response) => {
        if (error) {
          console.error(`GRPC CLIENT: Error en ${method}:`, error);
          console.error(`GRPC CLIENT: Error details:`, error.details);
          console.error(`GRPC CLIENT: Error code:`, error.code);
          reject(error);
        } else {
          console.log(`GRPC CLIENT: Success response from ${method}:`, JSON.stringify(response, null, 2));
          resolve(response);
        }
      });
    });
  };
};

// Cliente de usuarios con métodos promisificados
const userService = {
  createUser: promisifyGrpcCall(userClient, 'CreateUser'),
  getUser: promisifyGrpcCall(userClient, 'GetUser'),
  updateUser: promisifyGrpcCall(userClient, 'UpdateUser'),
  deleteUser: promisifyGrpcCall(userClient, 'DeleteUser'),
  listUsers: promisifyGrpcCall(userClient, 'ListUsers'),
  authenticateUser: promisifyGrpcCall(userClient, 'AuthenticateUser'),
};

// Cliente de inventario con métodos promisificados
const inventoryService = {
  createDonation: promisifyGrpcCall(inventoryClient, 'CreateDonation'),
  getDonation: promisifyGrpcCall(inventoryClient, 'GetDonation'),
  updateDonation: promisifyGrpcCall(inventoryClient, 'UpdateDonation'),
  deleteDonation: promisifyGrpcCall(inventoryClient, 'DeleteDonation'),
  listDonations: promisifyGrpcCall(inventoryClient, 'ListDonations'),
  transferDonations: promisifyGrpcCall(inventoryClient, 'TransferDonations'),
};

// Cliente de eventos con métodos promisificados
const eventsService = {
  createEvent: promisifyGrpcCall(eventsClient, 'CreateEvent'),
  getEvent: promisifyGrpcCall(eventsClient, 'GetEvent'),
  updateEvent: promisifyGrpcCall(eventsClient, 'UpdateEvent'),
  deleteEvent: promisifyGrpcCall(eventsClient, 'DeleteEvent'),
  listEvents: promisifyGrpcCall(eventsClient, 'ListEvents'),
  addParticipant: promisifyGrpcCall(eventsClient, 'AddParticipant'),
  removeParticipant: promisifyGrpcCall(eventsClient, 'RemoveParticipant'),
  listParticipants: promisifyGrpcCall(eventsClient, 'ListParticipants'),
  registerDistributedDonations: promisifyGrpcCall(eventsClient, 'RegisterDistributedDonations'),
  getDistributedDonations: promisifyGrpcCall(eventsClient, 'GetDistributedDonations'),
};

// Función para verificar conectividad de servicios
const checkServiceHealth = async () => {
  const services = [
    { name: 'User Service', url: USER_SERVICE_URL, client: userClient },
    { name: 'Inventory Service', url: INVENTORY_SERVICE_URL, client: inventoryClient },
    { name: 'Events Service', url: EVENTS_SERVICE_URL, client: eventsClient },
  ];

  const healthStatus = {};

  for (const service of services) {
    try {
      // Intentar una llamada simple para verificar conectividad
      // Nota: Esto es básico, en producción se implementarían health checks específicos
      healthStatus[service.name] = {
        status: 'unknown',
        url: service.url,
        message: 'Health check no implementado aún'
      };
    } catch (error) {
      healthStatus[service.name] = {
        status: 'error',
        url: service.url,
        message: error.message
      };
    }
  }

  return healthStatus;
};

module.exports = {
  userService,
  inventoryService,
  eventsService,
  checkServiceHealth,
  // Exportar clientes raw para casos especiales
  clients: {
    userClient,
    inventoryClient,
    eventsClient,
  },
  // Exportar enums para transformaciones
  enums: {
    UserRole: userProto.Role,
    DonationCategory: inventoryProto.Category,
  },
};