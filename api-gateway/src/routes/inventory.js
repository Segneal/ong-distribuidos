const express = require('express');
const { inventoryService } = require('../services/grpcClients');
const { inventoryTransformers, handleGrpcError, validateInput } = require('../utils/grpcMapper');
const { authenticateToken, requireRole, requirePermission } = require('../middleware/auth');
const router = express.Router();

// Aplicar autenticación a todas las rutas de inventario
router.use(authenticateToken);

// GET /api/inventory - PRESIDENTE y VOCAL
router.get('/', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { category, includeDeleted } = req.query;

    // Transformar filtros para gRPC
    const grpcRequest = inventoryTransformers.toGrpcListDonations({
      category,
      includeDeleted: includeDeleted === 'true'
    });

    // Llamar al microservicio de inventario
    const grpcResponse = await inventoryService.listDonations(grpcRequest);

    // Transformar respuesta
    const response = inventoryTransformers.fromGrpcDonationsList(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        donations: response.donations
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener inventario:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// GET /api/inventory/:id - PRESIDENTE y VOCAL
router.get('/:id', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { id } = req.params;

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de donación inválido'
      });
    }

    // Llamar al microservicio de inventario
    const grpcRequest = { id: parseInt(id) };
    const grpcResponse = await inventoryService.getDonation(grpcRequest);

    // Transformar respuesta
    const response = inventoryTransformers.fromGrpcDonationResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        donation: response.donation
      });
    } else {
      res.status(404).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al obtener donación:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// POST /api/inventory - PRESIDENTE y VOCAL
router.post('/', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const donationData = req.body;
    const userId = req.user?.id || 1; // TODO: Obtener del token de autenticación

    // Validar datos de entrada
    const validationErrors = validateInput.donation(donationData);
    if (validationErrors.length > 0) {
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Transformar datos para gRPC (usar usuario autenticado)
    const grpcRequest = inventoryTransformers.toGrpcCreateDonation(donationData, req.user.id);

    // Llamar al microservicio de inventario
    const grpcResponse = await inventoryService.createDonation(grpcRequest);

    // Transformar respuesta
    const response = inventoryTransformers.fromGrpcDonationResponse(grpcResponse);

    if (response.success) {
      res.status(201).json({
        success: true,
        message: response.message,
        donation: response.donation
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al crear donación:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// PUT /api/inventory/:id - PRESIDENTE y VOCAL
router.put('/:id', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { id } = req.params;
    const donationData = req.body;
    const userId = req.user?.id || 1; // TODO: Obtener del token de autenticación

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de donación inválido'
      });
    }

    // Validar datos de entrada (solo campos que se pueden actualizar)
    if (donationData.quantity && parseInt(donationData.quantity) < 0) {
      return res.status(400).json({
        error: 'La cantidad debe ser un número positivo'
      });
    }

    // Transformar datos para gRPC (usar usuario autenticado)
    const grpcRequest = inventoryTransformers.toGrpcUpdateDonation(id, donationData, req.user.id);

    // Llamar al microservicio de inventario
    const grpcResponse = await inventoryService.updateDonation(grpcRequest);

    // Transformar respuesta
    const response = inventoryTransformers.fromGrpcDonationResponse(grpcResponse);

    if (response.success) {
      res.status(200).json({
        success: true,
        message: response.message,
        donation: response.donation
      });
    } else {
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('Error al actualizar donación:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

// DELETE /api/inventory/:id - PRESIDENTE y VOCAL
router.delete('/:id', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user?.id || 1; // TODO: Obtener del token de autenticación

    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        error: 'ID de donación inválido'
      });
    }

    // Llamar al microservicio de inventario
    const grpcRequest = { 
      id: parseInt(id),
      deleted_by: userId
    };
    const grpcResponse = await inventoryService.deleteDonation(grpcRequest);

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
    console.error('Error al eliminar donación:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
});

module.exports = router;