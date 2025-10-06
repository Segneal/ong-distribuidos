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

    console.log(`🔍 INVENTORY ROUTE: User org = ${req.user.organization}`);

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
      // FILTRO FORZADO POR ORGANIZACIÓN
      const userOrganization = req.user.organization;
      const filteredDonations = response.donations.filter(donation => {
        const matches = donation.organization === userOrganization;
        console.log(`🔍 FILTER: ${donation.id} (${donation.organization}) === ${userOrganization} ? ${matches}`);
        return matches;
      });

      console.log(`🔍 FILTERED: ${filteredDonations.length} of ${response.donations.length} donations`);

      res.status(200).json({
        success: true,
        message: `Se encontraron ${filteredDonations.length} donaciones`,
        donations: filteredDonations
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
  console.log('=== POST /api/inventory STARTED ===');
  try {
    const donationData = req.body;
    const userId = req.user?.id || 1;

    console.log('1. POST /api/inventory - donationData:', JSON.stringify(donationData, null, 2));
    console.log('2. POST /api/inventory - userId:', userId);
    console.log('3. POST /api/inventory - user object:', JSON.stringify(req.user, null, 2));

    // Validar datos de entrada
    console.log('4. Starting validation...');
    const validationErrors = validateInput.donation(donationData);
    console.log('5. Validation errors:', validationErrors);
    if (validationErrors.length > 0) {
      console.log('6. Validation failed, returning 400');
      return res.status(400).json({
        error: 'Datos de entrada inválidos',
        details: validationErrors
      });
    }

    // Transformar datos para gRPC (usar usuario autenticado)
    console.log('7. Starting gRPC transformation...');
    console.log('7.1. User ID:', req.user.id);
    console.log('7.2. User Organization:', req.user.organization);
    
    const grpcRequest = inventoryTransformers.toGrpcCreateDonation(donationData, req.user.id, req.user.organization);
    console.log('8. gRPC request:', JSON.stringify(grpcRequest, null, 2));
    console.log('8.1. gRPC request organization field:', grpcRequest.organization);

    // Llamar al microservicio de inventario
    console.log('9. Calling inventory service...');
    const grpcResponse = await inventoryService.createDonation(grpcRequest);
    console.log('10. gRPC response:', JSON.stringify(grpcResponse, null, 2));

    // Transformar respuesta
    console.log('11. Transforming response...');
    const response = inventoryTransformers.fromGrpcDonationResponse(grpcResponse);
    console.log('12. Transformed response:', JSON.stringify(response, null, 2));

    if (response.success) {
      console.log('13. Success - returning 201');
      res.status(201).json({
        success: true,
        message: response.message,
        donation: response.donation
      });
    } else {
      console.log('14. Failed - returning 400 with message:', response.message);
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('15. EXCEPTION in POST /api/inventory:', error);
    console.error('16. Error stack:', error.stack);
    const errorResponse = handleGrpcError(error);
    console.log('17. Error response:', JSON.stringify(errorResponse, null, 2));
    res.status(errorResponse.status).json(errorResponse.error);
  }
  console.log('=== POST /api/inventory ENDED ===');
});

// PUT /api/inventory/:id - PRESIDENTE y VOCAL
router.put('/:id', requireRole(['PRESIDENTE', 'VOCAL']), async (req, res) => {
  console.log('=== PUT /api/inventory/:id STARTED ===');
  try {
    const { id } = req.params;
    const donationData = req.body;
    const userId = req.user?.id || 1; // TODO: Obtener del token de autenticación

    console.log('1. PUT /api/inventory - id:', id);
    console.log('2. PUT /api/inventory - donationData:', JSON.stringify(donationData, null, 2));
    console.log('3. PUT /api/inventory - userId:', userId);

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
    console.log('4. PUT /api/inventory - Calling toGrpcUpdateDonation...');
    const grpcRequest = inventoryTransformers.toGrpcUpdateDonation(id, donationData, req.user.id);
    console.log('5. PUT /api/inventory - grpcRequest:', JSON.stringify(grpcRequest, null, 2));

    // Llamar al microservicio de inventario
    console.log('6. PUT /api/inventory - Calling inventory service...');
    const grpcResponse = await inventoryService.updateDonation(grpcRequest);

    console.log('7. PUT /api/inventory - grpcResponse:', JSON.stringify(grpcResponse, null, 2));

    // Transformar respuesta
    console.log('8. PUT /api/inventory - Transforming response...');
    const response = inventoryTransformers.fromGrpcDonationResponse(grpcResponse);
    console.log('9. PUT /api/inventory - transformed response:', JSON.stringify(response, null, 2));

    if (response.success) {
      console.log('10. PUT /api/inventory - Success, returning 200');
      res.status(200).json({
        success: true,
        message: response.message,
        donation: response.donation
      });
    } else {
      console.log('11. PUT /api/inventory - Failed, returning 400');
      res.status(400).json({
        error: response.message
      });
    }
  } catch (error) {
    console.error('12. PUT /api/inventory - EXCEPTION:', error);
    const errorResponse = handleGrpcError(error);
    res.status(errorResponse.status).json(errorResponse.error);
  }
  console.log('=== PUT /api/inventory/:id ENDED ===');
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