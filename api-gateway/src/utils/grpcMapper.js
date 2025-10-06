// TRANSFORMADOR EXTREMADAMENTE SIMPLE - SIN COMPLICACIONES

// Mapeo de roles
const ROLE_MAPPING = {
  'PRESIDENTE': 0, 'VOCAL': 1, 'COORDINADOR': 2, 'VOLUNTARIO': 3,
  0: 'PRESIDENTE', 1: 'VOCAL', 2: 'COORDINADOR', 3: 'VOLUNTARIO',
};

// Mapeo de categorías
const CATEGORY_MAPPING = {
  'ROPA': 0, 'ALIMENTOS': 1, 'JUGUETES': 2, 'UTILES_ESCOLARES': 3,
  0: 'ROPA', 1: 'ALIMENTOS', 2: 'JUGUETES', 3: 'UTILES_ESCOLARES',
};

// Transformadores para usuarios
const userTransformers = {
  toGrpcCreateUser: (restUser) => ({
    username: restUser.username,
    first_name: restUser.firstName,
    last_name: restUser.lastName,
    email: restUser.email,
    phone: restUser.phone || '',
    role: ROLE_MAPPING[restUser.role] || 0,
    organization: restUser.organization || 'empuje-comunitario',
  }),

  toGrpcUpdateUser: (id, restUser) => ({
    id: parseInt(id),
    username: restUser.username,
    first_name: restUser.firstName,
    last_name: restUser.lastName,
    email: restUser.email,
    phone: restUser.phone || '',
    role: ROLE_MAPPING[restUser.role] || 0,
    organization: restUser.organization || 'empuje-comunitario',
  }),

  toGrpcAuth: (credentials) => ({
    username_or_email: credentials.usernameOrEmail,
    password: credentials.password,
  }),

  fromGrpcUser: (grpcUser) => {
    let role = 'VOLUNTARIO';
    if (typeof grpcUser.role === 'number') {
      role = ROLE_MAPPING[grpcUser.role] || 'VOLUNTARIO';
    } else if (typeof grpcUser.role === 'string') {
      role = grpcUser.role;
    }

    return {
      id: grpcUser.id,
      username: grpcUser.username,
      firstName: grpcUser.first_name,
      lastName: grpcUser.last_name,
      email: grpcUser.email,
      phone: grpcUser.phone,
      role,
      organization: grpcUser.organization,
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
  toGrpcCreateDonation: (restDonation, userId, userOrganization = 'empuje-comunitario') => {
    console.log('🔄 TRANSFORMER: toGrpcCreateDonation called');
    console.log('🔄 TRANSFORMER: restDonation:', JSON.stringify(restDonation, null, 2));
    console.log('🔄 TRANSFORMER: userId:', userId);
    console.log('🔄 TRANSFORMER: userOrganization:', userOrganization);
    
    const result = {
      category: CATEGORY_MAPPING[restDonation.category] || 0,
      description: restDonation.description || '',
      quantity: parseInt(restDonation.quantity) || 0,
      created_by: parseInt(userId),
      organization: userOrganization,
    };
    
    console.log('🔄 TRANSFORMER: result:', JSON.stringify(result, null, 2));
    return result;
  },

  toGrpcUpdateDonation: (id, restDonation, userId) => {
    console.log('TRANSFORMER: toGrpcUpdateDonation called');
    console.log('TRANSFORMER: id =', id);
    console.log('TRANSFORMER: restDonation =', JSON.stringify(restDonation, null, 2));
    console.log('TRANSFORMER: userId =', userId);
    console.log('TRANSFORMER: CATEGORY_MAPPING =', CATEGORY_MAPPING);

    const grpcRequest = {
      id: parseInt(id),
      description: restDonation.description || '',
      quantity: parseInt(restDonation.quantity) || 0,
      updated_by: parseInt(userId),
    };

    // Siempre agregar categoría (requerida en el proto)
    if (restDonation.category) {
      console.log('TRANSFORMER: Adding category:', restDonation.category);
      const mappedCategory = CATEGORY_MAPPING[restDonation.category];
      console.log('TRANSFORMER: Mapped category to:', mappedCategory);
      if (mappedCategory !== undefined) {
        grpcRequest.category = mappedCategory;
      } else {
        console.log('TRANSFORMER: Category not found in mapping, using 0 as default');
        grpcRequest.category = 0;
      }
    } else {
      console.log('TRANSFORMER: No category provided, using 0 as default');
      grpcRequest.category = 0;
    }

    console.log('TRANSFORMER: Final grpcRequest =', JSON.stringify(grpcRequest, null, 2));
    return grpcRequest;
  },

  toGrpcListDonations: (filters) => ({
    category: filters.category ? CATEGORY_MAPPING[filters.category] : undefined,
    include_deleted: filters.includeDeleted || false,
    organization: filters.organization || undefined,
  }),

  // FIX: soportar números, strings numéricos y strings de categoría
  fromGrpcDonation: (grpcDonation) => {
    let category = 'ROPA';
    const rawCategory = grpcDonation.category;

    const numCategory = parseInt(rawCategory);
    if (!isNaN(numCategory) && CATEGORY_MAPPING.hasOwnProperty(numCategory)) {
      category = CATEGORY_MAPPING[numCategory];
    } else if (typeof rawCategory === 'string') {
      category = rawCategory;
    }

    return {
      id: grpcDonation.id,
      category,
      description: grpcDonation.description,
      quantity: grpcDonation.quantity,
      organization: grpcDonation.organization || 'empuje-comunitario',
      deleted: grpcDonation.deleted,
      createdAt: grpcDonation.created_at,
      updatedAt: grpcDonation.updated_at,
      createdBy: grpcDonation.created_by,
      updatedBy: grpcDonation.updated_by,
    };
  },

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
  toGrpcCreateEvent: (restEvent, userOrganization = 'empuje-comunitario') => {
    console.log('🔄 EVENTS TRANSFORMER: toGrpcCreateEvent called');
    console.log('🔄 EVENTS TRANSFORMER: restEvent:', JSON.stringify(restEvent, null, 2));
    console.log('🔄 EVENTS TRANSFORMER: userOrganization:', userOrganization);
    
    const result = {
      name: restEvent.name,
      description: restEvent.description || '',
      event_date: restEvent.eventDate,
      participant_ids: restEvent.participantIds || [],
      organization: userOrganization,
    };
    
    console.log('🔄 EVENTS TRANSFORMER: result:', JSON.stringify(result, null, 2));
    return result;
  },

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

  fromGrpcEvent: (grpcEvent) => ({
    id: grpcEvent.id,
    name: grpcEvent.name,
    description: grpcEvent.description,
    eventDate: grpcEvent.event_date,
    organization: grpcEvent.organization || 'empuje-comunitario',
    createdAt: grpcEvent.created_at,
    updatedAt: grpcEvent.updated_at,
    expuesto_red: grpcEvent.expuesto_red !== undefined ? grpcEvent.expuesto_red : false,
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
    participants: grpcResponse.participants ? grpcResponse.participants.map(p => ({
      eventId: p.event_id,
      userId: p.user_id,
      userName: p.user_name,
      userLastName: p.user_last_name,
      adhesionDate: p.adhesion_date,
    })) : [],
  }),

  toGrpcRegisterDistributedDonations: (eventId, donationsData, registeredBy) => ({
    event_id: parseInt(eventId),
    donations: donationsData.map(donation => ({
      donation_id: parseInt(donation.donationId),
      quantity: parseInt(donation.quantity)
    })),
    registered_by: parseInt(registeredBy)
  }),

  fromGrpcDistributedDonation: (grpcDistributedDonation) => ({
    id: grpcDistributedDonation.id,
    eventId: grpcDistributedDonation.event_id,
    donationId: grpcDistributedDonation.donation_id,
    donationDescription: grpcDistributedDonation.donation_description,
    distributedQuantity: grpcDistributedDonation.distributed_quantity,
    registeredBy: grpcDistributedDonation.registered_by,
    registrationDate: grpcDistributedDonation.registration_date,
    registeredByName: grpcDistributedDonation.registered_by_name,
  }),

  fromGrpcDistributedDonationsResponse: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    distributedDonations: grpcResponse.distributed_donations ?
      grpcResponse.distributed_donations.map(eventsTransformers.fromGrpcDistributedDonation) : [],
  }),

  fromGrpcGetDistributedDonationsResponse: (grpcResponse) => ({
    success: grpcResponse.success,
    message: grpcResponse.message,
    distributedDonations: grpcResponse.distributed_donations ?
      grpcResponse.distributed_donations.map(eventsTransformers.fromGrpcDistributedDonation) : [],
  }),
};

// Función helper para manejar errores gRPC
const handleGrpcError = (error) => {
  const grpcToHttpStatus = {
    1: 499, 2: 500, 3: 400, 4: 504, 5: 404, 6: 409, 7: 403, 8: 429,
    9: 400, 10: 409, 11: 400, 12: 501, 13: 500, 14: 503, 15: 500, 16: 401,
  };

  const httpStatus = grpcToHttpStatus[error.code] || 500;
  const message = error.details || error.message || 'Error interno del servidor';

  return {
    status: httpStatus,
    error: { message, code: error.code, details: error.details },
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
      } else if (eventDate <= new Date()) {
        errors.push('La fecha del evento debe ser futura');
      }
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
