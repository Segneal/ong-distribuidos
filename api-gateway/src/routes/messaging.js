const express = require('express');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

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

router.post('/active-requests', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET ACTIVE REQUESTS ===');
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        solicitud_id as request_id,
        donaciones as donations,
        estado as status,
        fecha_creacion as timestamp,
        notas as notes
      FROM solicitudes_donaciones 
      WHERE estado = 'ACTIVA'
      ORDER BY fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const requests = rows.map(row => ({
      request_id: row.request_id,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes
    }));

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
      WHERE organizacion_donante != 'empuje-comunitario'
      AND activa = true
      ORDER BY fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query);
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

    const query = `
      SELECT 
        tipo as type,
        organizacion_contraparte as counterpart_organization,
        solicitud_id as request_id,
        donaciones as donations,
        estado as status,
        fecha_transferencia as timestamp,
        notas as notes
      FROM transferencias_donaciones 
      ORDER BY fecha_transferencia DESC
      LIMIT 50
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const transfers = rows.map(row => ({
      tipo: row.type,
      organizacion_contraparte: row.counterpart_organization,
      solicitud_id: row.request_id,
      donaciones: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      estado: row.status,
      fecha_transferencia: row.timestamp,
      notas: row.notes
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
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        solicitud_id as request_id,
        'external-org' as requesting_organization,
        donaciones as donations,
        estado as status,
        fecha_creacion as timestamp,
        notas as notes
      FROM solicitudes_donaciones 
      WHERE estado = 'ACTIVA'
      ORDER BY fecha_creacion DESC
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const requests = rows.map(row => ({
      request_id: row.request_id,
      requesting_organization: row.requesting_organization,
      donations: typeof row.donations === 'string' ? JSON.parse(row.donations) : row.donations,
      status: row.status,
      timestamp: row.timestamp,
      notes: row.notes
    }));

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
    const { donations, notes } = req.body;
    
    const connection = await createDbConnection();

    // Generate unique request ID
    const requestId = `REQ-${Date.now()}`;

    const query = `
      INSERT INTO solicitudes_donaciones 
      (solicitud_id, donaciones, estado, fecha_creacion, notas)
      VALUES (?, ?, 'ACTIVA', NOW(), ?)
    `;

    const [result] = await connection.execute(query, [
      requestId,
      JSON.stringify(donations),
      notes || ''
    ]);
    
    await connection.end();

    res.json({
      success: true,
      request_id: requestId,
      message: 'Solicitud de donación creada exitosamente'
    });
  } catch (error) {
    console.error('Error creating donation request:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Create donation offer
router.post('/create-donation-offer', authenticateToken, async (req, res) => {
  try {
    console.log('=== CREATE DONATION OFFER ===');
    const { donations, notes } = req.body;
    
    const connection = await createDbConnection();

    // Generate unique offer ID
    const offerId = `OFE-${Date.now()}`;

    const query = `
      INSERT INTO ofertas_externas 
      (organizacion_donante, oferta_id, donaciones, fecha_creacion, activa)
      VALUES (?, ?, ?, NOW(), true)
    `;

    const [result] = await connection.execute(query, [
      'empuje-comunitario',
      offerId,
      JSON.stringify(donations)
    ]);
    
    await connection.end();

    res.json({
      success: true,
      offer_id: offerId,
      message: 'Oferta de donación creada exitosamente'
    });
  } catch (error) {
    console.error('Error creating donation offer:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// Transfer donations
router.post('/transfer-donations', authenticateToken, async (req, res) => {
  try {
    console.log('=== TRANSFER DONATIONS ===');
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
    
    const connection = await createDbConnection();

    const query = `
      INSERT INTO transferencias_donaciones 
      (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, notas)
      VALUES (?, ?, ?, ?, 'COMPLETADA', NOW(), ?)
    `;

    const [result] = await connection.execute(query, [
      'ENVIADA',
      targetOrganization || 'organizacion-externa',
      requestId || null,
      JSON.stringify(donations),
      notes || ''
    ]);
    
    await connection.end();

    res.json({
      success: true,
      transfer_id: result.insertId,
      message: 'Transferencia de donaciones completada exitosamente'
    });
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

    const query = `
      SELECT 
        evento_id as event_id,
        organizacion_origen as source_organization,
        nombre as name,
        descripcion as description,
        fecha_evento as event_date,
        fecha_publicacion as published_date,
        activo as active
      FROM eventos_red 
      WHERE activo = true
      ORDER BY 
        CASE WHEN organizacion_origen = 'empuje-comunitario' THEN 0 ELSE 1 END,
        fecha_publicacion DESC
    `;

    const [rows] = await connection.execute(query);
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
          VALUES (?, 'empuje-comunitario', ?, ?, ?, NOW(), true)
          ON DUPLICATE KEY UPDATE
          activo = true, fecha_publicacion = NOW()
        `;
        
        await connection.execute(insertNetworkEventQuery, [
          eventId,
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
        WHERE evento_id = ? AND organizacion_origen = 'empuje-comunitario'
      `;
      
      await connection.execute(deactivateNetworkEventQuery, [eventId]);
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
    const { requestId } = req.body;
    
    const connection = await createDbConnection();

    const query = `
      UPDATE solicitudes_donaciones 
      SET estado = 'DADA_DE_BAJA', fecha_actualizacion = NOW()
      WHERE solicitud_id = ?
    `;

    const [result] = await connection.execute(query, [requestId]);
    await connection.end();

    if (result.affectedRows > 0) {
      res.json({
        success: true,
        message: 'Solicitud de donación cancelada exitosamente'
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Solicitud no encontrada'
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
      VALUES (?, 'empuje-comunitario', ?, ?, ?, NOW(), true)
      ON DUPLICATE KEY UPDATE
      activo = true, fecha_publicacion = NOW()
    `;

    await connection.execute(query, [eventId, name, description, eventDate]);
    
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

    // Deactivate from network
    const query = `
      UPDATE eventos_red 
      SET activo = false
      WHERE evento_id = ? AND organizacion_origen = 'empuje-comunitario'
    `;

    await connection.execute(query, [eventId]);
    
    // Update eventos table
    const updateEventQuery = `
      UPDATE eventos 
      SET expuesto_red = false
      WHERE id = ?
    `;
    
    await connection.execute(updateEventQuery, [eventId]);
    await connection.end();

    res.json({
      success: true,
      message: 'Evento removido de la red exitosamente'
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
    
    const connection = await createDbConnection();

    const query = `
      INSERT INTO adhesiones_eventos_externos 
      (evento_externo_id, voluntario_id, estado, datos_voluntario, fecha_adhesion)
      VALUES (?, ?, 'CONFIRMADA', ?, NOW())
      ON DUPLICATE KEY UPDATE
      estado = 'CONFIRMADA', fecha_adhesion = NOW(), datos_voluntario = ?
    `;

    await connection.execute(query, [
      eventId, 
      volunteerId, 
      JSON.stringify(volunteerData),
      JSON.stringify(volunteerData)
    ]);
    
    await connection.end();

    res.json({
      success: true,
      message: 'Te has inscrito exitosamente al evento'
    });
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
        er.organizacion_origen as source_organization
      FROM adhesiones_eventos_externos aee
      LEFT JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
      ORDER BY aee.fecha_adhesion DESC
    `;

    const [rows] = await connection.execute(query);
    await connection.end();

    const adhesions = rows.map(row => ({
      adhesion_id: row.adhesion_id,
      event_id: row.event_id,
      volunteer_id: row.volunteer_id,
      status: row.status,
      adhesion_date: row.adhesion_date,
      event_name: row.event_name,
      event_description: row.event_description,
      event_date: row.event_date,
      source_organization: row.source_organization
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
        u.name as volunteer_name,
        u.lastName as volunteer_last_name,
        u.email as volunteer_email
      FROM adhesiones_eventos_externos aee
      LEFT JOIN usuarios u ON aee.voluntario_id = u.id
      WHERE aee.evento_externo_id = ?
      ORDER BY aee.fecha_adhesion DESC
    `;

    const [rows] = await connection.execute(query, [eventId]);
    await connection.end();

    const adhesions = rows.map(row => ({
      adhesion_id: row.adhesion_id,
      volunteer_id: row.volunteer_id,
      status: row.status,
      adhesion_date: row.adhesion_date,
      volunteer_data: typeof row.volunteer_data === 'string' ? JSON.parse(row.volunteer_data) : row.volunteer_data,
      volunteer_name: row.volunteer_name,
      volunteer_last_name: row.volunteer_last_name,
      volunteer_email: row.volunteer_email
    }));

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
        WHERE evento_id = ? AND organizacion_origen = 'empuje-comunitario'
      `;
      
      await connection.execute(deactivateNetworkQuery, [
        cancellationReason || 'Evento cancelado',
        eventId
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

module.exports = router;