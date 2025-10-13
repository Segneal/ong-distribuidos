const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const axios = require('axios');

const router = express.Router();

// Configuración del messaging service
const MESSAGING_SERVICE_URL = process.env.MESSAGING_SERVICE_URL || 'http://localhost:50054';

// Helper function - localhost root root
async function createDbConnection() {
  const mysql = require('mysql2/promise');
  return await mysql.createConnection({
    host: 'localhost',
    database: 'ong_management',
    user: 'root',
    password: 'root',
    port: 3306,
    charset: 'utf8mb4'
  });
}

// POST /api/messaging/simulate-transfer-received - Simular transferencia recibida
router.post('/simulate-transfer-received', authenticateToken, async (req, res) => {
  try {
    console.log('=== SIMULATE TRANSFER RECEIVED ===');
    const { transferId, sourceOrg, targetOrg, requestId, donations } = req.body;
    
    if (!transferId || !sourceOrg || !targetOrg || !requestId || !donations) {
      return res.status(400).json({
        success: false,
        error: 'Faltan datos requeridos para simular transferencia'
      });
    }
    
    const connection = await createDbConnection();

    // 1. Crear transferencia RECIBIDA
    const insertQuery = `
      INSERT INTO transferencias_donaciones 
      (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
      VALUES (?, ?, ?, ?, ?, NOW(), ?, ?, ?)
    `;

    await connection.execute(insertQuery, [
      'RECIBIDA',
      sourceOrg,
      requestId,
      JSON.stringify(donations),
      'COMPLETADA',
      null, // usuario_registro
      `Transferencia recibida automáticamente - ${transferId}`,
      targetOrg
    ]);

    // 2. Crear notificación
    const notificationQuery = `
      INSERT INTO notificaciones 
      (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
      VALUES (?, ?, ?, ?, ?, false, NOW())
    `;

    // Buscar admin de la organización destino
    const userQuery = `
      SELECT id FROM usuarios 
      WHERE organizacion = ? AND rol IN ('PRESIDENTE', 'COORDINADOR') 
      LIMIT 1
    `;
    
    const [userRows] = await connection.execute(userQuery, [targetOrg]);
    
    if (userRows.length > 0) {
      const userId = userRows[0].id;
      const donationsList = donations.map(d => `• ${d.descripcion} (${d.cantidad})`).join('\n');
      
      await connection.execute(notificationQuery, [
        userId,
        'transferencia_recibida',
        '🎁 ¡Nueva donación recibida!',
        `Has recibido una donación de ${sourceOrg}:\n\n${donationsList}\n\nLas donaciones ya están disponibles en tu inventario.`,
        JSON.stringify({
          organizacion_origen: sourceOrg,
          request_id: requestId,
          cantidad_items: donations.length,
          transfer_id: transferId
        })
      ]);
    }

    await connection.end();

    res.json({
      success: true,
      message: 'Transferencia recibida simulada correctamente'
    });
    
  } catch (error) {
    console.error('Error simulating transfer received:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /api/messaging/transfer-history - Obtener historial de transferencias directamente de DB
router.get('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY DIRECT ===');
    const userOrg = req.user?.organization;
    const limit = parseInt(req.query.limit) || 50;
    
    if (!userOrg) {
      return res.status(401).json({
        success: false,
        error: 'Usuario no autenticado'
      });
    }
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        id,
        tipo,
        organizacion_contraparte,
        solicitud_id,
        donaciones,
        estado,
        fecha_transferencia,
        usuario_registro,
        notas,
        organizacion_propietaria
      FROM transferencias_donaciones 
      WHERE organizacion_propietaria = ?
      ORDER BY fecha_transferencia DESC
      LIMIT ?
    `;

    const [rows] = await connection.execute(query, [userOrg, limit.toString()]);
    await connection.end();

    // Procesar las transferencias
    const transfers = rows.map(row => {
      let donations = [];
      try {
        donations = typeof row.donaciones === 'string' ? JSON.parse(row.donaciones) : row.donaciones;
      } catch (e) {
        donations = [];
      }

      // Determinar source y target basado en tipo
      let source_org, target_org;
      if (row.tipo === 'ENVIADA') {
        source_org = userOrg;
        target_org = row.organizacion_contraparte;
      } else {
        source_org = row.organizacion_contraparte;
        target_org = userOrg;
      }

      return {
        id: row.id,
        transfer_id: `transfer-${row.id}`,
        tipo: row.tipo,
        source_organization: source_org,
        target_organization: target_org,
        organizacion_contraparte: row.organizacion_contraparte,
        request_id: row.solicitud_id,
        donations: donations,
        estado: row.estado,
        timestamp: row.fecha_transferencia ? row.fecha_transferencia.toISOString() : null,
        fecha_transferencia: row.fecha_transferencia ? row.fecha_transferencia.toISOString() : null,
        user_id: row.usuario_registro,
        notas: row.notas,
        organizacion_propietaria: row.organizacion_propietaria
      };
    });

    res.json({
      success: true,
      transfers: transfers
    });
    
  } catch (error) {
    console.error('Error getting transfer history:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');
    console.log('User organization:', req.user.organization);
    
    const connection = await createDbConnection();

    // Para empuje-comunitario, usar solicitudes_donaciones
    // Para otras organizaciones, usar solicitudes_externas
    let query, params;
    
    if (req.user.organization === 'empuje-comunitario') {
      query = `
        SELECT 
          solicitud_id as request_id,
          donaciones as donations,
          estado as status,
          fecha_creacion as timestamp,
          notas as notes
        FROM solicitudes_donaciones 
        WHERE estado = 'ACTIVA'
        AND organization_id = ?
        ORDER BY fecha_creacion DESC
      `;
      params = [req.user.organization];
    } else {
      query = `
        SELECT 
          solicitud_id as request_id,
          donaciones as donations,
          activa as status,
          fecha_creacion as timestamp,
          '' as notes
        FROM solicitudes_externas 
        WHERE activa = 1
        AND organizacion_solicitante = ?
        ORDER BY fecha_creacion DESC
      `;
      params = [req.user.organization];
    }

    const [rows] = await connection.execute(query, params);
    await connection.end();

    const requests = rows.map(row => ({
      request_id: row.request_id,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes || ''
    }));

    console.log(`Found ${requests.length} active requests for organization: ${req.user.organization}`);

    res.json({
      success: true,
      requests: requests
    });
  } catch (error) {
    console.error('Error getting active requests:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// GET /api/messaging/my-offers - Obtener mis ofertas
router.get('/my-offers', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET MY OFFERS ===');
    console.log('User organization:', req.user.organization);
    
    const response = await axios.get(`${MESSAGING_SERVICE_URL}/api/getMyOffers`, {
      params: {
        organization: req.user.organization
      }
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error getting my offers:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

// POST /api/messaging/deactivate-offer - Desactivar oferta
router.post('/deactivate-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== DEACTIVATE OFFER ===');
    console.log('User organization:', req.user.organization);
    console.log('Offer ID:', req.body.offerId);
    
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/deactivateOffer`, {
      offerId: req.body.offerId,
      organization: req.user.organization
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error deactivating offer:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

router.post('/external-offers', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL OFFERS ===');
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        oferta_id as offer_id,
        organizacion_donante as organization_id,
        organizacion_donante as organization_name,
        donaciones as donations,
        fecha_creacion as timestamp,
        activa as active
      FROM ofertas_externas 
      WHERE organizacion_donante != ?
      AND activa = true
      ORDER BY fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query, [req.user.organization]);
    await connection.end();

    const offers = rows.map(row => ({
      offer_id: row.offer_id,
      donor_organization: row.organization_id,
      organization_name: row.organization_name,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      timestamp: row.timestamp,
      active: row.active
    }));

    res.json({
      success: true,
      offers: offers
    });
  } catch (error) {
    console.error('Error getting external offers:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

router.post('/transfer-history', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET TRANSFER HISTORY ===');
    
    const connection = await createDbConnection();

    const userOrganization = req.user.organization;
    
    const query = `
      SELECT 
        tipo as type,
        organizacion_contraparte as counterpart_organization,
        solicitud_id as request_id,
        donaciones as donations,
        estado as status,
        fecha_transferencia as timestamp,
        notas as notes,
        organizacion_propietaria as owner_organization
      FROM transferencias_donaciones 
      WHERE organizacion_propietaria = ?
      ORDER BY fecha_transferencia DESC
      LIMIT 50
    `;

    const [rows] = await connection.execute(query, [userOrganization]);
    await connection.end();

    const transfers = rows.map(row => ({
      tipo: row.type,
      organizacion_contraparte: row.counterpart_organization,
      solicitud_id: row.request_id,
      donaciones: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      estado: row.status,
      fecha_transferencia: row.timestamp,
      notas: row.notes,
      organizacion_propietaria: row.owner_organization
    }));

    res.json({
      success: true,
      transfers: transfers
    });
  } catch (error) {
    console.error('Error getting transfer history:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// External requests route
router.post('/external-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL REQUESTS ===');
    console.log('User organization:', req.user.organization);
    
    const connection = await createDbConnection();

    // Obtener solicitudes de otras organizaciones desde solicitudes_externas
    const query = `
      SELECT 
        se.solicitud_id as request_id,
        se.organizacion_solicitante as requesting_organization,
        se.donaciones as donations,
        se.activa as status,
        se.fecha_creacion as timestamp,
        '' as notes
      FROM solicitudes_externas se
      WHERE se.activa = 1
      AND se.organizacion_solicitante != ?
      ORDER BY se.fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query, [req.user.organization]);
    await connection.end();

    const requests = rows.map(row => ({
      request_id: row.request_id,
      requesting_organization: row.requesting_organization,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes
    }));

    console.log(`Found ${requests.length} external requests`);

    res.json({
      success: true,
      requests: requests
    });
  } catch (error) {
    console.error('Error getting external requests:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Create donation request
router.post('/create-donation-request', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION REQUEST ===');
    console.log('User organization:', req.user.organization);
    
    const { donations, notes } = req.body;
    
    // Call messaging service
    const axios = require('axios');
    const messagingResponse = await axios.post(`${MESSAGING_SERVICE_URL}/api/createDonationRequest`, {
      donations: donations,
      userId: req.user.id,
      userOrganization: req.user.organization,
      notes: notes || ''
    });

    if (messagingResponse.data.success) {
      res.json({
        success: true,
        request_id: messagingResponse.data.request_id,
        message: messagingResponse.data.message
      });
    } else {
      res.status(400).json({
        success: false,
        error: messagingResponse.data.message || 'Error creating donation request'
      });
    }
  } catch (error) {
    console.error('Error creating donation request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.response?.data?.detail || error.message
    });
  }
});

// Create donation offer
router.post('/create-donation-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION OFFER ===');
    console.log('User organization:', req.user.organization);
    
    const { donations, notes } = req.body;
    
    // Call messaging service
    const axios = require('axios');
    const messagingResponse = await axios.post(`${MESSAGING_SERVICE_URL}/api/createDonationOffer`, {
      donations: donations,
      userId: req.user.id,
      userOrganization: req.user.organization,
      notes: notes || ''
    });

    if (messagingResponse.data.success) {
      res.json({
        success: true,
        offer_id: messagingResponse.data.offer_id,
        message: messagingResponse.data.message
      });
    } else {
      res.status(400).json({
        success: false,
        error: messagingResponse.data.message || 'Error creating donation offer'
      });
    }
  } catch (error) {
    console.error('Error creating donation offer:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.response?.data?.detail || error.message
    });
  }
});

// Transfer donations
router.post('/transfer-donations', authenticateToken, async (req, res) => {
  try {
    console.log('=== TRANSFER DONATIONS ===');
    console.log('User organization:', req.user.organization);
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    const { targetOrganization, requestId, donations, notes } = req.body;
    
    // Validate required fields
    if (!targetOrganization || !donations || !Array.isArray(donations)) {
      return res.status(400).json({
        success: false,
        error: 'Datos de transferencia inválidos',
        message: 'targetOrganization y donations son requeridos'
      });
    }
    
    // Create transfer directly in database
    const connection = await createDbConnection();
    
    try {
      // Insert ENVIADA transfer
      const [result] = await connection.execute(`
        INSERT INTO transferencias_donaciones 
        (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
        VALUES (?, ?, ?, ?, ?, NOW(), ?, ?, ?)
      `, [
        'ENVIADA',
        targetOrganization,
        requestId || `direct-${Date.now()}`,
        JSON.stringify(donations),
        'COMPLETADA',
        req.user.userId || req.user.id,
        notes || 'Transferencia directa',
        req.user.organization
      ]);
      
      const transferId = result.insertId;
      console.log(`Transfer created with ID: ${transferId}`);
      
      await connection.end();
      
      // Automatically process pending transfers after successful transfer
      try {
        console.log('Auto-processing pending transfers...');
        const axios = require('axios');
        const processResponse = await axios.post(`http://localhost:3001/api/messaging/process-pending-transfers`);
        console.log('Auto-processing result:', processResponse.data);
      } catch (processError) {
        console.error('Error auto-processing transfers:', processError.message);
        // Don't fail the main request if auto-processing fails
      }
      
      res.json({
        success: true,
        transfer_id: `transfer-${transferId}`,
        message: 'Transferencia completada exitosamente'
      });
      
    } catch (dbError) {
      await connection.end();
      throw dbError;
    }
  } catch (error) {
    console.error('Error transferring donations:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Get external events
router.post('/external-events', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EXTERNAL EVENTS ===');
    
    const connection = await createDbConnection();

    const userOrganization = req.user.organization;
    
    const query = `
      SELECT 
        er.evento_id as event_id,
        er.organizacion_origen as source_organization,
        e.nombre as name,
        e.descripcion as description,
        e.fecha_evento as event_date,
        er.fecha_publicacion as published_date,
        er.activo as active
      FROM eventos_red er
      JOIN eventos e ON er.evento_id = e.id
      WHERE er.activo = true
      AND er.organizacion_origen != ?
      ORDER BY er.fecha_publicacion DESC
    `;

    const [rows] = await connection.execute(query, [userOrganization]);
    await connection.end();

    const events = rows.map(row => ({
      event_id: row.event_id,
      source_organization: row.source_organization,
      name: row.name,
      description: row.description,
      event_date: row.event_date,
      published_date: row.published_date,
      active: row.active
    }));

    res.json({
      success: true,
      events: events
    });
  } catch (error) {
    console.error('Error getting external events:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Toggle event exposure
router.post('/toggle-event-exposure', authenticateToken, async (req, res) => {
  try {
    console.log('=== TOGGLE EVENT EXPOSURE ===');
    const { eventId, expuesto_red } = req.body;
    console.log(`User organization: ${req.user.organization}`);
    console.log(`Event ID: ${eventId}, Expose: ${expuesto_red}`);
    
    const connection = await createDbConnection();

    // First update the eventos table
    const updateEventQuery = `
      UPDATE eventos 
      SET expuesto_red = ?
      WHERE id = ?
    `;

    await connection.execute(updateEventQuery, [expuesto_red, eventId]);

    // If exposing to network, insert into eventos_red table
    if (expuesto_red) {
      // Get event details first
      const getEventQuery = `
        SELECT nombre as name, descripcion as description, fecha_evento as eventDate 
        FROM eventos 
        WHERE id = ?
      `;
      
      const [eventRows] = await connection.execute(getEventQuery, [eventId]);
      
      if (eventRows.length > 0) {
        const event = eventRows[0];
        
        // Insert or update in eventos_red
        const insertNetworkEventQuery = `
          INSERT INTO eventos_red 
          (evento_id, organizacion_origen, nombre, descripcion, fecha_evento, fecha_publicacion, activo)
          VALUES (?, ?, ?, ?, ?, NOW(), true)
          ON DUPLICATE KEY UPDATE
          activo = true, fecha_publicacion = NOW()
        `;
        
        await connection.execute(insertNetworkEventQuery, [
          eventId,
          req.user.organization, // Usar la organización del usuario logueado
          event.name,
          event.description,
          event.eventDate
        ]);
      }
    } else {
      // Remove from network or mark as inactive
      const deactivateNetworkEventQuery = `
        UPDATE eventos_red 
        SET activo = false
        WHERE evento_id = ? AND organizacion_origen = ?
      `;
      
      await connection.execute(deactivateNetworkEventQuery, [eventId, req.user.organization]);
    }
    
    await connection.end();

    res.json({
      success: true,
      message: expuesto_red ? 'Evento expuesto a la red' : 'Evento removido de la red'
    });
  } catch (error) {
    console.error('Error toggling event exposure:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Cancel donation request
router.post('/cancel-donation-request', authenticateToken, async (req, res) => {
  try {
    console.log('=== CANCEL DONATION REQUEST ===');
    console.log('User organization:', req.user.organization);
    const { requestId } = req.body;
    
    if (!requestId) {
      return res.status(400).json({
        success: false,
        error: 'Request ID es requerido'
      });
    }
    
    const connection = await createDbConnection();
    let result;

    // Para empuje-comunitario, actualizar solicitudes_donaciones
    // Para otras organizaciones, actualizar solicitudes_externas
    if (req.user.organization === 'empuje-comunitario') {
      const query = `
        UPDATE solicitudes_donaciones 
        SET estado = 'DADA_DE_BAJA', fecha_actualizacion = NOW()
        WHERE solicitud_id = ? AND organization_id = ?
      `;
      [result] = await connection.execute(query, [requestId, req.user.organization]);
    } else {
      const query = `
        UPDATE solicitudes_externas 
        SET activa = 0
        WHERE solicitud_id = ? AND organizacion_solicitante = ?
      `;
      [result] = await connection.execute(query, [requestId, req.user.organization]);
    }
    
    await connection.end();

    if (result.affectedRows > 0) {
      res.json({
        success: true,
        message: 'Solicitud de donación cancelada exitosamente'
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Solicitud no encontrada o no pertenece a su organización'
      });
    }
  } catch (error) {
    console.error('Error canceling donation request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Publish event to network
router.post('/publish-event', authenticateToken, async (req, res) => {
  try {
    console.log('=== PUBLISH EVENT ===');
    const { eventId, name, description, eventDate } = req.body;
    
    const connection = await createDbConnection();

    // Insert into eventos_red
    const query = `
      INSERT INTO eventos_red 
      (evento_id, organizacion_origen, nombre, descripcion, fecha_evento, fecha_publicacion, activo)
      VALUES (?, ?, ?, ?, ?, NOW(), true)
      ON DUPLICATE KEY UPDATE
      activo = true, fecha_publicacion = NOW()
    `;

    await connection.execute(query, [eventId, req.user.organization, name, description, eventDate]);
    
    // Update eventos table to mark as exposed
    const updateEventQuery = `
      UPDATE eventos 
      SET expuesto_red = true
      WHERE id = ?
    `;
    
    await connection.execute(updateEventQuery, [eventId]);
    await connection.end();

    res.json({
      success: true,
      message: 'Evento publicado en la red exitosamente'
    });
  } catch (error) {
    console.error('Error publishing event:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Cancel event from network
router.post('/cancel-event', authenticateToken, async (req, res) => {
  try {
    console.log('=== CANCEL EVENT ===');
    const { eventId } = req.body;
    
    const connection = await createDbConnection();

    try {
      // 1. Obtener información del evento antes de cancelarlo
      const eventInfoQuery = `
        SELECT e.nombre, e.descripcion, er.organizacion_origen
        FROM eventos e
        JOIN eventos_red er ON e.id = er.evento_id
        WHERE e.id = ? AND er.organizacion_origen = ?
      `;
      
      const [eventRows] = await connection.execute(eventInfoQuery, [eventId, req.user.organization]);
      
      if (eventRows.length === 0) {
        await connection.end();
        return res.status(404).json({
          success: false,
          error: 'Evento no encontrado o no pertenece a su organización'
        });
      }
      
      const eventInfo = eventRows[0];
      
      // 2. Obtener todos los voluntarios que se habían anotado
      const adhesionsQuery = `
        SELECT aee.voluntario_id, aee.datos_voluntario, u.nombre, u.apellido, u.email
        FROM adhesiones_eventos_externos aee
        JOIN usuarios u ON aee.voluntario_id = u.id
        WHERE aee.evento_externo_id = ? AND aee.estado IN ('PENDIENTE', 'CONFIRMADA')
      `;
      
      const [adhesionRows] = await connection.execute(adhesionsQuery, [eventId]);
      
      // 3. Desactivar el evento de la red
      const deactivateQuery = `
        UPDATE eventos_red 
        SET activo = false
        WHERE evento_id = ? AND organizacion_origen = ?
      `;
      
      await connection.execute(deactivateQuery, [eventId, req.user.organization]);
      
      // 4. Actualizar la tabla eventos
      const updateEventQuery = `
        UPDATE eventos 
        SET expuesto_red = false
        WHERE id = ?
      `;
      
      await connection.execute(updateEventQuery, [eventId]);
      
      // 5. Cancelar todas las adhesiones pendientes y aprobadas
      const cancelAdhesionsQuery = `
        UPDATE adhesiones_eventos_externos 
        SET estado = 'CANCELADA'
        WHERE evento_externo_id = ? AND estado IN ('PENDIENTE', 'CONFIRMADA')
      `;
      
      await connection.execute(cancelAdhesionsQuery, [eventId]);
      
      // 6. Crear notificaciones para todos los voluntarios afectados
      if (adhesionRows.length > 0) {
        const notificationQuery = `
          INSERT INTO notificaciones 
          (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
          VALUES (?, ?, ?, ?, ?, false, NOW())
        `;
        
        for (const adhesion of adhesionRows) {
          const volunteerName = `${adhesion.nombre} ${adhesion.apellido}`;
          const title = "❌ Evento cancelado";
          const message = `Lamentamos informarte que el evento "${eventInfo.nombre}" de ${eventInfo.organizacion_origen} ha sido cancelado y removido de la red.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.`;
          
          await connection.execute(notificationQuery, [
            adhesion.voluntario_id,
            'evento_cancelado',
            title,
            message,
            JSON.stringify({
              evento_id: eventId,
              evento_nombre: eventInfo.nombre,
              organizacion_origen: eventInfo.organizacion_origen,
              fecha_cancelacion: new Date().toISOString()
            })
          ]);
        }
        
        console.log(`Notificaciones enviadas a ${adhesionRows.length} voluntarios`);
      }
      
      await connection.end();

      res.json({
        success: true,
        message: 'Evento removido de la red exitosamente',
        notifications_sent: adhesionRows.length,
        adhesions_cancelled: adhesionRows.length
      });
      
    } catch (dbError) {
      await connection.end();
      throw dbError;
    }
  } catch (error) {
    console.error('Error canceling event:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Create event adhesion
router.post('/create-event-adhesion', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE EVENT ADHESION ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    const { eventId, targetOrganization, volunteerData } = req.body;
    
    // Validate required fields
    if (!eventId || !volunteerData) {
      return res.status(400).json({
        success: false,
        error: 'Datos de adhesión inválidos',
        message: 'eventId y volunteerData son requeridos'
      });
    }
    
    // Use authenticated user's ID as volunteer ID
    const volunteerId = req.user?.id || 1; // Fallback to 1 if no user in token
    
    // Create adhesion directly in database
    const connection = await createDbConnection();
    
    try {
      // Check if adhesion already exists
      const checkQuery = `
        SELECT id FROM adhesiones_eventos_externos 
        WHERE evento_externo_id = ? AND voluntario_id = ?
      `;
      
      const [existingRows] = await connection.execute(checkQuery, [eventId, volunteerId]);
      
      if (existingRows.length > 0) {
        await connection.end();
        return res.status(400).json({
          success: false,
          error: 'Ya tienes una adhesión a este evento'
        });
      }
      
      // Create new adhesion
      const insertQuery = `
        INSERT INTO adhesiones_eventos_externos 
        (evento_externo_id, voluntario_id, fecha_adhesion, estado, datos_voluntario)
        VALUES (?, ?, NOW(), 'PENDIENTE', ?)
      `;
      
      await connection.execute(insertQuery, [
        eventId,
        volunteerId,
        JSON.stringify(volunteerData)
      ]);
      
      // Get event details and organization admin for notification
      const eventQuery = `
        SELECT er.nombre as event_name, er.organizacion_origen,
               u.id as admin_id
        FROM eventos_red er
        LEFT JOIN usuarios u ON u.organizacion = er.organizacion_origen 
                             AND u.rol IN ('PRESIDENTE', 'COORDINADOR')
        WHERE er.evento_id = ?
        ORDER BY CASE WHEN u.rol = 'PRESIDENTE' THEN 1 ELSE 2 END
        LIMIT 1
      `;
      
      const [eventRows] = await connection.execute(eventQuery, [eventId]);
      
      if (eventRows.length > 0) {
        const eventData = eventRows[0];
        
        // Create notification for event organizer
        const notificationQuery = `
          INSERT INTO notificaciones 
          (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
          VALUES (?, ?, ?, ?, NOW(), false)
        `;
        
        const title = "🎯 Nueva solicitud de adhesión a evento";
        const message = `${volunteerData.nombre} quiere participar en tu evento '${eventData.event_name}'. Revisa la solicitud en la sección de adhesiones.`;
        
        await connection.execute(notificationQuery, [
          eventData.admin_id,
          title,
          message,
          'adhesion_evento'
        ]);
      }
      
      await connection.end();
      
      res.json({
        success: true,
        message: 'Tu solicitud de adhesión ha sido enviada y está pendiente de aprobación'
      });
      
    } catch (dbError) {
      await connection.end();
      throw dbError;
    }
  } catch (error) {
    console.error('Error creating event adhesion:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Get volunteer adhesions
router.post('/volunteer-adhesions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET VOLUNTEER ADHESIONS ===');
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        aee.id as adhesion_id,
        aee.evento_externo_id as event_id,
        aee.voluntario_id as volunteer_id,
        aee.estado as status,
        aee.fecha_adhesion as adhesion_date,
        er.nombre as event_name,
        er.descripcion as event_description,
        er.fecha_evento as event_date,
        er.organizacion_origen as organization_id
      FROM adhesiones_eventos_externos aee
      LEFT JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      WHERE aee.voluntario_id = ?
      ORDER BY aee.fecha_adhesion DESC
    `;

    const [rows] = await connection.execute(query, [req.user.id]);
    await connection.end();

    const adhesions = rows.map(row => ({
      id: row.adhesion_id,
      event_id: row.event_id,
      event_name: row.event_name || 'Evento no encontrado',
      event_description: row.event_description || '',
      event_date: row.event_date,
      organization_id: row.organization_id || 'Organización no especificada',
      adhesion_date: row.adhesion_date,
      status: row.status
    }));

    res.json({
      success: true,
      adhesions: adhesions
    });
  } catch (error) {
    console.error('Error getting volunteer adhesions:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Get event adhesions
router.post('/event-adhesions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET EVENT ADHESIONS ===');
    const { eventId } = req.body;
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        aee.id as adhesion_id,
        aee.voluntario_id as volunteer_id,
        aee.estado as status,
        aee.fecha_adhesion as adhesion_date,
        aee.datos_voluntario as volunteer_data,
        u.nombre as volunteer_name,
        u.apellido as volunteer_surname,
        u.email as volunteer_email,
        u.telefono as volunteer_phone
      FROM adhesiones_eventos_externos aee
      LEFT JOIN usuarios u ON aee.voluntario_id = u.id
      WHERE aee.evento_externo_id = ?
      ORDER BY aee.fecha_adhesion DESC
    `;

    const [rows] = await connection.execute(query, [eventId]);
    await connection.end();

    const adhesions = rows.map(row => {
      let volunteerData = {};
      try {
        volunteerData = typeof row.volunteer_data === 'string' ? JSON.parse(row.volunteer_data) : row.volunteer_data || {};
      } catch (e) {
        console.warn('Error parsing volunteer_data:', e);
        volunteerData = {};
      }

      return {
        id: row.adhesion_id,
        adhesion_id: row.adhesion_id,
        volunteer_id: row.volunteer_id,
        status: row.status,
        adhesion_date: row.adhesion_date,
        volunteer_name: row.volunteer_name || volunteerData.name || 'No especificado',
        volunteer_surname: row.volunteer_surname || volunteerData.surname || 'No especificado',
        volunteer_email: row.volunteer_email || volunteerData.email || 'No especificado',
        volunteer_phone: row.volunteer_phone || volunteerData.phone || 'No especificado',
        organization_id: volunteerData.organization_id || 'No especificada',
        external_volunteer: volunteerData.organization_id && volunteerData.organization_id !== req.user.organizacion
      };
    });

    res.json({
      success: true,
      adhesions: adhesions
    });
  } catch (error) {
    console.error('Error getting event adhesions:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Cancel event and notify network
router.post('/cancel-own-event', authenticateToken, async (req, res) => {
  try {
    console.log('=== CANCEL OWN EVENT ===');
    const { eventId, cancellationReason } = req.body;
    
    if (!eventId) {
      return res.status(400).json({
        success: false,
        error: 'Event ID es requerido'
      });
    }
    
    const connection = await createDbConnection();

    // Verificar que el evento existe y pertenece a nuestra organización
    const checkEventQuery = `
      SELECT id, nombre, fecha_evento, expuesto_red
      FROM eventos 
      WHERE id = ?
    `;
    
    const [eventRows] = await connection.execute(checkEventQuery, [eventId]);
    
    if (eventRows.length === 0) {
      await connection.end();
      return res.status(404).json({
        success: false,
        error: 'Evento no encontrado'
      });
    }
    
    const event = eventRows[0];
    
    // Marcar evento como cancelado en nuestra BD
    const cancelEventQuery = `
      UPDATE eventos 
      SET descripcion = CONCAT(COALESCE(descripcion, ''), ' - CANCELADO: ', ?),
          expuesto_red = false
      WHERE id = ?
    `;
    
    await connection.execute(cancelEventQuery, [
      cancellationReason || 'Evento cancelado',
      eventId
    ]);
    
    // Si el evento estaba expuesto a la red, desactivarlo
    if (event.expuesto_red) {
      const deactivateNetworkQuery = `
        UPDATE eventos_red 
        SET activo = false,
            descripcion = CONCAT(descripcion, ' - CANCELADO: ', ?)
        WHERE evento_id = ? AND organizacion_origen = ?
      `;
      
      await connection.execute(deactivateNetworkQuery, [
        cancellationReason || 'Evento cancelado',
        eventId,
        req.user.organization
      ]);
      
      // TODO: Enviar mensaje a Kafka topic /baja-evento-solidario
      // Aquí se integraría con el messaging service
      console.log(`Evento ${eventId} cancelado y notificado a la red`);
    }
    
    await connection.end();

    res.json({
      success: true,
      message: 'Evento cancelado exitosamente',
      wasExposed: event.expuesto_red
    });
    
  } catch (error) {
    console.error('Error canceling event:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// ==========================================
// RUTAS PARA SOLICITUDES DE INSCRIPCIÓN
// ==========================================

// POST /api/messaging/inscription-request - Crear solicitud de inscripción
router.post('/inscription-request', async (req, res) => {
  try {
    console.log('=== CREATE INSCRIPTION REQUEST ===');
    console.log('Request body:', req.body);
    
    const { nombre, apellido, email, telefono, organizacion_destino, rol_solicitado, mensaje } = req.body;
    
    // Validaciones básicas
    if (!nombre || !apellido || !email || !organizacion_destino || !rol_solicitado) {
      return res.status(400).json({
        success: false,
        error: 'Campos requeridos: nombre, apellido, email, organizacion_destino, rol_solicitado'
      });
    }
    
    if (!['COORDINADOR', 'VOLUNTARIO'].includes(rol_solicitado)) {
      return res.status(400).json({
        success: false,
        error: 'Rol solicitado debe ser COORDINADOR o VOLUNTARIO'
      });
    }
    
    // Llamar al messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/inscription-request`, {
      nombre,
      apellido,
      email,
      telefono,
      organizacion_destino,
      rol_solicitado,
      mensaje
    });
    
    res.json(response.data);
    
  } catch (error) {
    console.error('Error creating inscription request:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

// GET /api/messaging/pending-inscriptions - Obtener solicitudes pendientes (PRESIDENTE/VOCAL)
router.get('/pending-inscriptions', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET PENDING INSCRIPTIONS ===');
    console.log('User:', req.user);
    
    // Verificar que el usuario tenga permisos
    if (!['PRESIDENTE', 'VOCAL'].includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: 'Solo PRESIDENTE y VOCAL pueden ver solicitudes de inscripción'
      });
    }
    
    // Llamar al messaging service
    const response = await axios.get(`${MESSAGING_SERVICE_URL}/api/pending-inscriptions`, {
      params: {
        organizacion: req.user.organization,
        usuario_id: req.user.id
      }
    });
    
    res.json(response.data);
    
  } catch (error) {
    console.error('Error getting pending inscriptions:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

// POST /api/messaging/process-inscription - Procesar solicitud (aprobar/denegar)
router.post('/process-inscription', authenticateToken, async (req, res) => {
  try {
    console.log('=== PROCESS INSCRIPTION ===');
    console.log('User:', req.user);
    console.log('Request body:', req.body);
    
    const { solicitud_id, accion, comentarios } = req.body;
    
    // Validaciones
    if (!solicitud_id || !accion) {
      return res.status(400).json({
        success: false,
        error: 'Campos requeridos: solicitud_id, accion'
      });
    }
    
    if (!['APROBAR', 'DENEGAR'].includes(accion)) {
      return res.status(400).json({
        success: false,
        error: 'Acción debe ser APROBAR o DENEGAR'
      });
    }
    
    // Verificar permisos
    if (!['PRESIDENTE', 'VOCAL'].includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: 'Solo PRESIDENTE y VOCAL pueden procesar solicitudes'
      });
    }
    
    // Llamar al messaging service
    const response = await axios.post(`${MESSAGING_SERVICE_URL}/api/process-inscription`, {
      solicitud_id,
      accion,
      comentarios,
      usuario_revisor: {
        id: req.user.id,
        nombre: req.user.username,
        rol: req.user.role
      }
    });
    
    res.json(response.data);
    
  } catch (error) {
    console.error('Error processing inscription:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

// GET /api/messaging/inscription-notifications - Obtener notificaciones de inscripción
router.get('/inscription-notifications', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET INSCRIPTION NOTIFICATIONS ===');
    console.log('User:', req.user);
    
    // Verificar permisos
    if (!['PRESIDENTE', 'VOCAL'].includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: 'Solo PRESIDENTE y VOCAL pueden ver notificaciones de inscripción'
      });
    }
    
    // Llamar al messaging service
    const response = await axios.get(`${MESSAGING_SERVICE_URL}/api/inscription-notifications`, {
      params: {
        usuario_id: req.user.id
      }
    });
    
    res.json(response.data);
    
  } catch (error) {
    console.error('Error getting inscription notifications:', error);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
      });
    }
  }
});

// Approve event adhesion
router.post('/approve-event-adhesion', authenticateToken, async (req, res) => {
  try {
    console.log('=== APPROVE EVENT ADHESION ===');
    const { adhesionId } = req.body;
    
    if (!adhesionId) {
      return res.status(400).json({
        success: false,
        error: 'ID de adhesión es requerido'
      });
    }
    
    const connection = await createDbConnection();

    // Verificar que la adhesión existe y está pendiente
    const checkQuery = `
      SELECT aee.id, aee.estado, er.organizacion_origen
      FROM adhesiones_eventos_externos aee
      JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      WHERE aee.id = ?
    `;
    
    const [checkRows] = await connection.execute(checkQuery, [adhesionId]);
    
    if (checkRows.length === 0) {
      await connection.end();
      return res.status(404).json({
        success: false,
        error: 'Adhesión no encontrada'
      });
    }
    
    const adhesion = checkRows[0];
    
    // Verificar que el usuario pertenece a la organización del evento
    if (adhesion.organizacion_origen !== req.user.organization) {
      await connection.end();
      return res.status(403).json({
        success: false,
        error: 'No tiene permisos para aprobar esta adhesión'
      });
    }
    
    if (adhesion.estado !== 'PENDIENTE') {
      await connection.end();
      return res.status(400).json({
        success: false,
        error: 'La adhesión ya ha sido procesada'
      });
    }
    
    // Obtener datos de la adhesión antes de aprobar
    const getAdhesionQuery = `
      SELECT aee.voluntario_id, aee.datos_voluntario, er.nombre as event_name
      FROM adhesiones_eventos_externos aee
      JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      WHERE aee.id = ?
    `;
    
    const [adhesionRows] = await connection.execute(getAdhesionQuery, [adhesionId]);
    const adhesionData = adhesionRows[0];
    
    // Aprobar la adhesión
    const updateQuery = `
      UPDATE adhesiones_eventos_externos 
      SET estado = 'CONFIRMADA', fecha_aprobacion = NOW()
      WHERE id = ?
    `;
    
    await connection.execute(updateQuery, [adhesionId]);
    
    // Crear notificación para el voluntario
    if (adhesionData) {
      const notificationQuery = `
        INSERT INTO notificaciones 
        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
        VALUES (?, ?, ?, ?, NOW(), false)
      `;
      
      const title = "✅ Adhesión a evento aprobada";
      const message = `¡Genial! Tu solicitud para participar en '${adhesionData.event_name}' ha sido aprobada. ¡Nos vemos en el evento!`;
      
      await connection.execute(notificationQuery, [
        adhesionData.voluntario_id,
        title,
        message,
        'adhesion_evento'
      ]);
    }
    
    await connection.end();

    res.json({
      success: true,
      message: 'Adhesión aprobada exitosamente'
    });
  } catch (error) {
    console.error('Error approving event adhesion:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Reject event adhesion
router.post('/reject-event-adhesion', authenticateToken, async (req, res) => {
  try {
    console.log('=== REJECT EVENT ADHESION ===');
    const { adhesionId, reason } = req.body;
    
    if (!adhesionId) {
      return res.status(400).json({
        success: false,
        error: 'ID de adhesión es requerido'
      });
    }
    
    const connection = await createDbConnection();

    // Verificar que la adhesión existe y está pendiente
    const checkQuery = `
      SELECT aee.id, aee.estado, er.organizacion_origen
      FROM adhesiones_eventos_externos aee
      JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      WHERE aee.id = ?
    `;
    
    const [checkRows] = await connection.execute(checkQuery, [adhesionId]);
    
    if (checkRows.length === 0) {
      await connection.end();
      return res.status(404).json({
        success: false,
        error: 'Adhesión no encontrada'
      });
    }
    
    const adhesion = checkRows[0];
    
    // Verificar que el usuario pertenece a la organización del evento
    if (adhesion.organizacion_origen !== req.user.organization) {
      await connection.end();
      return res.status(403).json({
        success: false,
        error: 'No tiene permisos para rechazar esta adhesión'
      });
    }
    
    if (adhesion.estado !== 'PENDIENTE') {
      await connection.end();
      return res.status(400).json({
        success: false,
        error: 'La adhesión ya ha sido procesada'
      });
    }
    
    // Obtener datos de la adhesión antes de rechazar
    const getAdhesionQuery = `
      SELECT aee.voluntario_id, aee.datos_voluntario, er.nombre as event_name
      FROM adhesiones_eventos_externos aee
      JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      WHERE aee.id = ?
    `;
    
    const [adhesionRows] = await connection.execute(getAdhesionQuery, [adhesionId]);
    const adhesionData = adhesionRows[0];
    
    // Rechazar la adhesión
    const updateQuery = `
      UPDATE adhesiones_eventos_externos 
      SET estado = 'RECHAZADA', fecha_aprobacion = NOW(), motivo_rechazo = ?
      WHERE id = ?
    `;
    
    await connection.execute(updateQuery, [reason || 'Sin motivo especificado', adhesionId]);
    
    // Crear notificación para el voluntario
    if (adhesionData) {
      const notificationQuery = `
        INSERT INTO notificaciones 
        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
        VALUES (?, ?, ?, ?, NOW(), false)
      `;
      
      const title = "❌ Adhesión a evento rechazada";
      let message = `Tu solicitud para participar en '${adhesionData.event_name}' no fue aprobada.`;
      if (reason) {
        message += ` Motivo: ${reason}`;
      }
      
      await connection.execute(notificationQuery, [
        adhesionData.voluntario_id,
        title,
        message,
        'adhesion_evento'
      ]);
    }
    
    await connection.end();

    res.json({
      success: true,
      message: 'Adhesión rechazada exitosamente'
    });
  } catch (error) {
    console.error('Error rejecting event adhesion:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// POST /api/messaging/process-pending-transfers - Procesar transferencias pendientes automáticamente
router.post('/process-pending-transfers', async (req, res) => {
  try {
    const connection = await createDbConnection();
    
    // Buscar transferencias ENVIADAS que no tienen su contraparte RECIBIDA
    const [pendingTransfers] = await connection.execute(`
      SELECT t1.* FROM transferencias_donaciones t1
      WHERE t1.tipo = 'ENVIADA' 
      AND t1.fecha_transferencia > DATE_SUB(NOW(), INTERVAL 1 HOUR)
      AND NOT EXISTS (
        SELECT 1 FROM transferencias_donaciones t2 
        WHERE t2.tipo = 'RECIBIDA' 
        AND t2.solicitud_id = t1.solicitud_id 
        AND t2.organizacion_contraparte = t1.organizacion_propietaria
        AND t2.organizacion_propietaria = t1.organizacion_contraparte
      )
      ORDER BY t1.fecha_transferencia DESC
    `);
    
    console.log(`Processing ${pendingTransfers.length} pending transfers`);
    
    for (const transfer of pendingTransfers) {
      // Crear transferencia RECIBIDA
      await connection.execute(`
        INSERT INTO transferencias_donaciones 
        (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
        VALUES (?, ?, ?, ?, ?, NOW(), NULL, ?, ?)
      `, [
        'RECIBIDA',
        transfer.organizacion_propietaria,  // Quien envió
        transfer.solicitud_id,
        transfer.donaciones,
        'COMPLETADA',
        'Transferencia recibida automáticamente - procesada por consumer automático',
        transfer.organizacion_contraparte  // Quien recibe
      ]);
      
      // Buscar admin de la organización receptora
      const [userRows] = await connection.execute(`
        SELECT id FROM usuarios 
        WHERE organizacion = ? AND rol IN ('PRESIDENTE', 'COORDINADOR') 
        LIMIT 1
      `, [transfer.organizacion_contraparte]);
      
      if (userRows.length > 0) {
        const targetUserId = userRows[0].id;
        
        // Parsear donaciones
        let donations = [];
        try {
          donations = typeof transfer.donaciones === 'string' ? JSON.parse(transfer.donaciones) : transfer.donaciones;
        } catch (e) {
          donations = [];
        }
        
        const donationsText = donations.map(d => 
          `• ${d.descripcion || d.description || 'Donación'} (${d.cantidad || d.quantity || '1'})`
        ).join('\n');
        
        // Crear notificación
        await connection.execute(`
          INSERT INTO notificaciones 
          (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
          VALUES (?, ?, ?, ?, ?, false, NOW())
        `, [
          targetUserId,
          'transferencia_recibida',
          '🎁 ¡Nueva donación recibida!',
          `Has recibido una donación de ${transfer.organizacion_propietaria}:\n\n${donationsText}\n\nLas donaciones ya están disponibles en tu inventario.`,
          JSON.stringify({
            organizacion_origen: transfer.organizacion_propietaria,
            request_id: transfer.solicitud_id,
            cantidad_items: donations.length,
            transfer_id: `auto-${transfer.id}`
          })
        ]);
      }
    }
    
    await connection.end();
    
    res.json({
      success: true,
      processed: pendingTransfers.length,
      message: `Procesadas ${pendingTransfers.length} transferencias pendientes`
    });
    
  } catch (error) {
    console.error('Error processing pending transfers:', error);
    res.status(500).json({
      success: false,
      error: 'Error procesando transferencias pendientes',
      message: error.message
    });
  }
});

// POST /api/messaging/contact-offer - Contactar sobre una oferta
router.post('/contact-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== CONTACT OFFER ===');
    const { offerId, targetOrganization, message } = req.body;
    
    if (!offerId || !targetOrganization) {
      return res.status(400).json({
        success: false,
        error: 'ID de oferta y organización destino son requeridos'
      });
    }
    
    const connection = await createDbConnection();
    
    try {
      // Verificar que la oferta existe
      const offerQuery = `
        SELECT oferta_id, organizacion_donante, donaciones
        FROM ofertas_externas 
        WHERE oferta_id = ? AND organizacion_donante = ? AND activa = true
      `;
      
      const [offerRows] = await connection.execute(offerQuery, [offerId, targetOrganization]);
      
      if (offerRows.length === 0) {
        await connection.end();
        return res.status(404).json({
          success: false,
          error: 'Oferta no encontrada o no activa'
        });
      }
      
      const offer = offerRows[0];
      
      // Obtener admin de la organización que tiene la oferta (targetOrganization)
      const targetAdminQuery = `
        SELECT id, nombre, apellido
        FROM usuarios 
        WHERE organizacion = ? AND rol IN ('PRESIDENTE', 'COORDINADOR')
        ORDER BY CASE WHEN rol = 'PRESIDENTE' THEN 1 ELSE 2 END
        LIMIT 1
      `;
      
      const [targetAdminRows] = await connection.execute(targetAdminQuery, [targetOrganization]);
      
      if (targetAdminRows.length > 0) {
        const targetAdmin = targetAdminRows[0];
        
        // Crear notificación para la organización que tiene la oferta
        const targetNotificationQuery = `
          INSERT INTO notificaciones 
          (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
          VALUES (?, ?, ?, ?, NOW(), false)
        `;
        
        const targetTitle = "📞 Solicitud de contacto por oferta";
        const targetMessage = `${req.user.organization} está interesada en su oferta de donaciones (ID: ${offerId}). ${message ? 'Mensaje: ' + message : 'Quieren coordinar la obtención de las donaciones.'}`;
        
        await connection.execute(targetNotificationQuery, [
          targetAdmin.id,
          targetTitle,
          targetMessage,
          'solicitud_donacion'
        ]);
      }
      
      // Crear notificación para quien solicita el contacto
      const senderNotificationQuery = `
        INSERT INTO notificaciones 
        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
        VALUES (?, ?, ?, ?, NOW(), false)
      `;
      
      const senderTitle = "✅ Solicitud de contacto enviada";
      const senderMessage = `Hemos notificado a ${targetOrganization} sobre su interés en la oferta ${offerId}. Deberían contactarlos pronto para coordinar la obtención de las donaciones.`;
      
      await connection.execute(senderNotificationQuery, [
        req.user.id,
        senderTitle,
        senderMessage,
        'solicitud_donacion'
      ]);
      
      await connection.end();
      
      res.json({
        success: true,
        message: 'Solicitud de contacto enviada exitosamente'
      });
      
    } catch (dbError) {
      await connection.end();
      throw dbError;
    }
    
  } catch (error) {
    console.error('Error contacting about offer:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

module.exports = router;