const express = require('express');
const { userService } = require('../services/grpcClients');
const { userTransformers, handleGrpcError, validateInput } = require('../utils/grpcMapper');
const { authenticateToken, requireRole, requirePermission } = require('../middleware/auth');
const router = express.Router();

// Aplicar autenticación a todas las rutas de usuarios
router.use(authenticateToken);

// GET /api/users - Solo PRESIDENTE
router.get('/', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const { includeInactive } = req.query;

    // Llamar al microservicio de usuarios
    const grpcRequest = { include_inactive: includeInactive === 'true' };
    const grpcResponse = await userService.listUsers(grpcRequest);

    // Transformar respuesta
    const response = userTransformers.fromGrpcUsersList(grpcResponse);

    if (response.success) {
      // Filtrar usuarios por organización del usuario logueado
      const userOrganization = req.user.organization;
      console.log(`=== USERS FILTER DEBUG ===`);
      console.log(`User organization: ${userOrganization}`);
      console.log(`Total users from service: ${response.users.length}`);
      
      const filteredUsers = response.users.filter(user => {
        console.log(`User ${user.username}: ${user.organization} === ${userOrganization} ? ${user.organization === userOrganization}`);
        return user.organization === userOrganization;
      });
      
      console.log(`Filtered users: ${filteredUsers.length}`);
      
      res.status(200).json({
        success: true,
        message: `Se encontraron ${filteredUsers.length} usuarios de ${userOrganization}`,
        users: filteredUsers
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener usuarios:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// GET /api/users/:id - Solo PRESIDENTE
router.get('/:id', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de usuario inválido'
      });
    }

    // Llamar al microservicio de usuarios
    const grpcRequest = { id: parseInt(id) };
    const grpcResponse = await userService.getUser(grpcRequest);

    // Transformar respuesta
    const response = userTransformers.fromGrpcUserResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        user: response.user
      });
    } else {
      res.status(404).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener usuario:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// POST /api/users - Solo PRESIDENTE
router.post('/', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const userData = req.body;

    // Validar datos de entrada
    const validationErrors = validateInput.user(userData);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Forzar la organización del usuario logueado
    userData.organization = req.user.organization;
    
    // Transformar datos para gRPC
    const grpcRequest = userTransformers.toGrpcCreateUser(userData);

    // Llamar al microservicio de usuarios
    const grpcResponse = await userService.createUser(grpcRequest);

    // Transformar respuesta
    const response = userTransformers.fromGrpcUserResponse(grpcResponse);

    if (response.success) {
      res.status(201).json({
        success: true,
        message: response.message,
        user: response.user
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al crear usuario:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// PUT /api/users/:id - Solo PRESIDENTE
router.put('/:id', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const { id } = req.params;
    const userData = req.body;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de usuario inválido'
      });
    }

    // Validar datos de entrada
    const validationErrors = validateInput.user(userData);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Transformar datos para gRPC
    const grpcRequest = userTransformers.toGrpcUpdateUser(id, userData);

    // Llamar al microservicio de usuarios
    const grpcResponse = await userService.updateUser(grpcRequest);

    // Transformar respuesta
    const response = userTransformers.fromGrpcUserResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        user: response.user
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al actualizar usuario:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// DELETE /api/users/:id - Solo PRESIDENTE
router.delete('/:id', requireRole(['PRESIDENTE']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de usuario inválido'
      });
    }

    // Llamar al microservicio de usuarios
    const grpcRequest = { id: parseInt(id) };
    const grpcResponse = await userService.deleteUser(grpcRequest);

    if (grpcResponse.success) {
      res.status(200).json({
        success: true,
        message: grpcResponse.message
      });
    } else {
      res.status(400).json({
        error: grpcResponse.message
      });
    }
  } catch (error) {
    console.error('Error al eliminar usuario:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

module.exports = router;