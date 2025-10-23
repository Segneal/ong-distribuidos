const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { authenticateToken, requireRole } = require('../middleware/auth');

const router = express.Router();

// Configuración del reports service
const REPORTS_SERVICE_URL = process.env.REPORTS_SERVICE_URL || 'http://localhost:8002';

// Middleware de autenticación para todas las rutas de reportes
router.use(authenticateToken);

// Proxy para GraphQL - /api/graphql
// GraphQL maneja reportes de donaciones (PRESIDENTE, VOCAL) y eventos (todos los usuarios)
const graphqlProxy = createProxyMiddleware('/graphql', {
    target: REPORTS_SERVICE_URL,
    changeOrigin: true,
    onProxyReq: (proxyReq, req, res) => {
        // Agregar información del usuario autenticado a los headers
        if (req.user) {
            proxyReq.setHeader('X-User-ID', req.user.userId || req.user.id);
            proxyReq.setHeader('X-User-Organization', req.user.organization);
            proxyReq.setHeader('X-User-Role', req.user.role);
        }
    },
    onError: (err, req, res) => {
        console.error('GraphQL Proxy Error:', err);
        res.status(503).json({
            success: false,
            error: 'Reports service unavailable',
            message: 'El servicio de reportes no está disponible'
        });
    }
});

// Proxy para rutas REST de reportes - /api/reports/*
// Exportación Excel para donaciones (PRESIDENTE, VOCAL)
const reportsProxy = createProxyMiddleware({
    target: REPORTS_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api/reports': '/api/reports'
    },
    onProxyReq: (proxyReq, req, res) => {
        // Agregar información del usuario autenticado a los headers
        if (req.user) {
            proxyReq.setHeader('X-User-ID', req.user.userId || req.user.id);
            proxyReq.setHeader('X-User-Organization', req.user.organization);
            proxyReq.setHeader('X-User-Role', req.user.role);
        }
    },
    onError: (err, req, res) => {
        console.error('Reports Proxy Error:', err);
        res.status(503).json({
            success: false,
            error: 'Reports service unavailable',
            message: 'El servicio de reportes no está disponible'
        });
    }
});

// Proxy para gestión de filtros - /api/filters/*
// Filtros para donaciones (PRESIDENTE, VOCAL) y eventos (todos los usuarios)
const filtersProxy = createProxyMiddleware({
    target: REPORTS_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api/filters': '/api/filters'
    },
    onProxyReq: (proxyReq, req, res) => {
        // Agregar información del usuario autenticado a los headers
        if (req.user) {
            proxyReq.setHeader('X-User-ID', req.user.userId || req.user.id);
            proxyReq.setHeader('X-User-Organization', req.user.organization);
            proxyReq.setHeader('X-User-Role', req.user.role);
        }
    },
    onError: (err, req, res) => {
        console.error('Filters Proxy Error:', err);
        res.status(503).json({
            success: false,
            error: 'Reports service unavailable',
            message: 'El servicio de filtros no está disponible'
        });
    }
});

// Proxy para consulta de red - /api/network/*
// Solo para PRESIDENTES según requerimiento 6
const networkProxy = createProxyMiddleware({
    target: REPORTS_SERVICE_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api/network': '/api/network'
    },
    onProxyReq: (proxyReq, req, res) => {
        // Agregar información del usuario autenticado a los headers
        if (req.user) {
            proxyReq.setHeader('X-User-ID', req.user.userId || req.user.id);
            proxyReq.setHeader('X-User-Organization', req.user.organization);
            proxyReq.setHeader('X-User-Role', req.user.role);
        }
    },
    onError: (err, req, res) => {
        console.error('Network Proxy Error:', err);
        res.status(503).json({
            success: false,
            error: 'Reports service unavailable',
            message: 'El servicio de consulta de red no está disponible'
        });
    }
});

// Aplicar los proxies a las rutas correspondientes con validación de roles

// GraphQL - Todos los usuarios autenticados (el servicio maneja la lógica de permisos internamente)
router.use(graphqlProxy);

// Reportes REST - Solo PRESIDENTE y VOCAL para exportación Excel de donaciones
router.use('/reports', requireRole(['PRESIDENTE', 'VOCAL']), reportsProxy);

// Filtros - Todos los usuarios autenticados (el servicio maneja la lógica de permisos internamente)
router.use('/filters', filtersProxy);

// Consulta de red SOAP - Solo PRESIDENTES
router.use('/network', requireRole(['PRESIDENTE']), networkProxy);

module.exports = router;