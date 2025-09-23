// Mapeo de roles entre REST y gRPC
const ROLE_MAPPING = {
  // REST -> gRPC
  'PRESIDENTE': 0,
  'VOCAL': 1,
  'COORDINADOR': 2,
  'VOLUNTARIO': 3,
  // gRPC -> REST
  0: 'PRESIDENTE',
  1: 'VOCAL',
  2: 'COORDINADOR',
  3: 'VOLUNTARIO',
};

// Mapeo de categorías entre REST y gRPC
const CATEGORY_MAPPING = {
  // REST -> gRPC
  'ROPA': 0,
  'ALIMENTOS': 1,
  'JUGUETES': 2,
  'UTILES_ESCOLARES': 3,
  // gRPC -> REST
  0: 'ROPA',
  1: 'ALIMENTOS',
  2: 'JUGUETES',
  3: 'UTILES_ESCOLARES',
};

// Transformadores para usuarios
const userTransformers = {
  // REST -> gRPC
  toGrpcCreateUser: (restUser) => ({
    username: restUser.username,
    first_name: restUser.firstName,
    last_name: restUser.lastName,
    email: restUser.email,
    phone: restUser.phone || '',
    role: ROLE_MAPPING[restUser.role] || 0,
  }),

  toGrpcUpdateUser: (id, restUser) => ({
    id: parseInt(id),
    username: restUser.username,
    first_name: restUser.firstName,
    last_name: restUser.lastName,
    email: restUser.email,
    phone: restUser.phone || '',
    role: ROLE_MAPPING[restUser.role] || 0,
  }),

  toGrpcAuth: (credentials) => ({
    username_or_email: credentials.usernameOrEmail,
    password: credentials.password,
  }),

  // gRPC -> REST
  fromGrpcUser: (grpcUser) => {
    // Manejar tanto números (enum) como strings
    let role = 'VOLUNTARIO'; // valor por defecto

    if (typeof grpcUser.role === 'number') {
      // Si viene como número (enum correcto)
      role = ROLE_MAPPING[grpcUser.role] || 'VOLUNTARIO';
    } else if (typeof grpcUser.role === 'string') {
      // Si viene como string (fallback)
      role = grpcUser.role;
    }

    return {
      id: grpcUser.id,
      username: grpcUser.username,
      firstName: grpcUser.first_name,
      lastName: grpcUser.last_name,
      email: grpcUser.email,
      phone: grpcUser.phone,
      role: role,
      isActive: grpcUser.is_active,
      createdAt: grpcUser.created_at,
      updatedAt: grpcUser.updated_at,
    };
  },

  fromGrpcUserResponse: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    user: grpcResponse.user ? userTransformers.fromGrpcUser(grpcResponse.user) : null,
    token: grpcResponse.token || null,
  }),

  fromGrpcUsersList: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    users: grpcResponse.users ? grpcResponse.users.map(userTransformers.fromGrpcUser) : [],
  }),
};

// Transformadores para inventario
const inventoryTransformers = {
  // REST -> gRPC
  toGrpcCreateDonation: (restDonation, userId) => ({
    category: CATEGORY_MAPPING[restDonation.category] || 0,
    description: restDonation.description || '',
    quantity: parseInt(restDonation.quantity) || 0,
    created_by: parseInt(userId),
  }),

  toGrpcUpdateDonation: (id, restDonation, userId) => ({
    id: parseInt(id),
    description: restDonation.description || '',
    quantity: parseInt(restDonation.quantity) || 0,
    updated_by: parseInt(userId),
  }),

  toGrpcListDonations: (filters) => ({
    category: filters.category ? CATEGORY_MAPPING[filters.category] : undefined,
    include_deleted: filters.includeDeleted || false,
  }),

  // gRPC -> REST
  fromGrpcDonation: (grpcDonation) => ({
    id: grpcDonation.id,
    category: CATEGORY_MAPPING[grpcDonation.category] || 'ROPA',
    description: grpcDonation.description,
    quantity: grpcDonation.quantity,
    deleted: grpcDonation.deleted,
    createdAt: grpcDonation.created_at,
    updatedAt: grpcDonation.updated_at,
    createdBy: grpcDonation.created_by,
    updatedBy: grpcDonation.updated_by,
  }),

  fromGrpcDonationResponse: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    donation: grpcResponse.donation ? inventoryTransformers.fromGrpcDonation(grpcResponse.donation) : null,
  }),

  fromGrpcDonationsList: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    donations: grpcResponse.donations ? grpcResponse.donations.map(inventoryTransformers.fromGrpcDonation) : [],
  }),
};

// Transformadores para eventos
const eventsTransformers = {
  // REST -> gRPC
  toGrpcCreateEvent: (restEvent) => ({
    name: restEvent.name,
    description: restEvent.description || '',
    event_date: restEvent.eventDate,
    participant_ids: restEvent.participantIds || [],
  }),

  toGrpcUpdateEvent: (id, restEvent) => ({
    id: parseInt(id),
    name: restEvent.name,
    description: restEvent.description || '',
    event_date: restEvent.eventDate,
  }),

  toGrpcListEvents: (filters) => ({
    include_past_events: filters.includePastEvents || false,
    user_id: filters.userId ? parseInt(filters.userId) : undefined,
  }),

  toGrpcAddParticipant: (eventId, userId) => ({
    event_id: parseInt(eventId),
    user_id: parseInt(userId),
  }),

  // gRPC -> REST
  fromGrpcEvent: (grpcEvent) => ({
    id: grpcEvent.id,
    name: grpcEvent.name,
    description: grpcEvent.description,
    eventDate: grpcEvent.event_date,
    createdAt: grpcEvent.created_at,
    updatedAt: grpcEvent.updated_at,
  }),

  fromGrpcParticipant: (grpcParticipant) => ({
    eventId: grpcParticipant.event_id,
    userId: grpcParticipant.user_id,
    userName: grpcParticipant.user_name,
    userLastName: grpcParticipant.user_last_name,
    adhesionDate: grpcParticipant.adhesion_date,
  }),

  fromGrpcEventResponse: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    event: grpcResponse.event ? eventsTransformers.fromGrpcEvent(grpcResponse.event) : null,
  }),

  fromGrpcEventsList: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    events: grpcResponse.events ? grpcResponse.events.map(eventsTransformers.fromGrpcEvent) : [],
  }),

  fromGrpcParticipantsList: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    participants: grpcResponse.participants ? grpcResponse.participants.map(eventsTransformers.fromGrpcParticipant) : [],
  }),
};

// Función helper para manejar errores gRPC
const handleGrpcError = (error) => {
  console.error('gRPC Error:', error);

  // Mapear códigos de error gRPC a códigos HTTP
  const grpcToHttpStatus = {
    1: 499, // CANCELLED
    2: 500, // UNKNOWN
    3: 400, // INVALID_ARGUMENT
    4: 504, // DEADLINE_EXCEEDED
    5: 404, // NOT_FOUND
    6: 409, // ALREADY_EXISTS
    7: 403, // PERMISSION_DENIED
    8: 429, // RESOURCE_EXHAUSTED
    9: 400, // FAILED_PRECONDITION
    10: 409, // ABORTED
    11: 400, // OUT_OF_RANGE
    12: 501, // UNIMPLEMENTED
    13: 500, // INTERNAL
    14: 503, // UNAVAILABLE
    15: 500, // DATA_LOSS
    16: 401, // UNAUTHENTICATED
  };

  const httpStatus = grpcToHttpStatus[error.code] || 500;
  const message = error.details || error.message || 'Error interno del servidor';

  return {
    status: httpStatus,
    error: {
      message,
      code: error.code,
      details: error.details,
    },
  };
};

// Función helper para validar datos de entrada
const validateInput = {
  user: (userData) => {
    const errors = [];

    if (!userData.username || userData.username.trim().length < 3) {
      errors.push('El nombre de usuario debe tener al menos 3 caracteres');
    }

    if (!userData.firstName || userData.firstName.trim().length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres');
    }

    if (!userData.lastName || userData.lastName.trim().length < 2) {
      errors.push('El apellido debe tener al menos 2 caracteres');
    }

    if (!userData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userData.email)) {
      errors.push('El email debe tener un formato válido');
    }

    if (!userData.role || !Object.keys(ROLE_MAPPING).includes(userData.role)) {
      errors.push('El rol debe ser válido (PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO)');
    }

    return errors;
  },

  donation: (donationData) => {
    const errors = [];

    if (!donationData.category || !Object.keys(CATEGORY_MAPPING).includes(donationData.category)) {
      errors.push('La categoría debe ser válida (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)');
    }

    if (!donationData.quantity || parseInt(donationData.quantity) < 0) {
      errors.push('La cantidad debe ser un número positivo');
    }

    return errors;
  },

  event: (eventData) => {
    const errors = [];

    if (!eventData.name || eventData.name.trim().length < 3) {
      errors.push('El nombre del evento debe tener al menos 3 caracteres');
    }

    if (!eventData.eventDate) {
      errors.push('La fecha del evento es requerida');
    } else {
      const eventDate = new Date(eventData.eventDate);
      if (isNaN(eventDate.getTime())) {
        errors.push('La fecha del evento debe tener un formato válido');
      }
    }

    return errors;
  },
};

module.exports = {
  userTransformers,
  inventoryTransformers,
  eventsTransformers,
  handleGrpcError,
  validateInput,
  ROLE_MAPPING,
  CATEGORY_MAPPING,
};