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

// GET /api/notifications - Obtener notificaciones del usuario
router.get('/', authenticateToken, async (req, res) => {
  try {
    console.log('=== GET NOTIFICATIONS ===');
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({
        success: false,
        error: 'Usuario no autenticado'
      });
    }
    
    const connection = await createDbConnection();

    const query = `
      SELECT 
        id,
        titulo,
        mensaje,
        tipo,
        fecha_creacion,
        fecha_lectura,
        leida
      FROM notificaciones 
      WHERE usuario_id = ?
      ORDER BY fecha_creacion DESC
      LIMIT 50
    `;

    const [rows] = await connection.execute(query, [userId]);
    await connection.end();

    res.json({
      success: true,
      notifications: rows
    });
    
  } catch (error) {
    console.error('Error getting notifications:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// PUT /api/notifications/:id/read - Marcar notificación como leída
router.put('/:id/read', authenticateToken, async (req, res) => {
  try {
    console.log('=== MARK NOTIFICATION AS READ ===');
    const { id } = req.params;
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({
        success: false,
        error: 'Usuario no autenticado'
      });
    }
    
    const connection = await createDbConnection();

    const query = `
      UPDATE notificaciones 
      SET leida = true, fecha_lectura = NOW()
      WHERE id = ? AND usuario_id = ?
    `;

    const [result] = await connection.execute(query, [id, userId]);
    await connection.end();

    if (result.affectedRows > 0) {
      res.json({
        success: true,
        message: 'Notificación marcada como leída'
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Notificación no encontrada'
      });
    }
    
  } catch (error) {
    console.error('Error marking notification as read:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

// PUT /api/notifications/read-all - Marcar todas las notificaciones como leídas
router.put('/read-all', authenticateToken, async (req, res) => {
  try {
    console.log('=== MARK ALL NOTIFICATIONS AS READ ===');
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({
        success: false,
        error: 'Usuario no autenticado'
      });
    }
    
    const connection = await createDbConnection();

    const query = `
      UPDATE notificaciones 
      SET leida = true, fecha_lectura = NOW()
      WHERE usuario_id = ? AND leida = false
    `;

    const [result] = await connection.execute(query, [userId]);
    await connection.end();

    res.json({
      success: true,
      message: `${result.affectedRows} notificaciones marcadas como leídas`
    });
    
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error.message
    });
  }
});

module.exports = router;