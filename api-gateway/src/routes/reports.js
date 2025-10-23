const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { authenticateToken, requireRole } = require('../middleware/auth');

const router = express.Router();

// Configuración del reports service
const REPORTS_SERVICE_URL = process.env.REPORTS_SERVICE_URL || 'http://localhost:8002';

// Middleware de autenticación para todas las rutas de reportes
router.use((req, res, next) => {
    console.log(`[REPORTS] ${req.method} ${req.url} - Before auth`);
    next();
});

router.use(authenticateToken);

router.use((req, res, next) => {
    console.log(`[REPORTS] ${req.method} ${req.url} - After auth, user:`, req.user ? req.user.id : 'NO USER');
    next();
});

// Proxy para GraphQL - /api/graphql
// GraphQL maneja reportes de donaciones (PRESIDENTE, VOCAL) y eventos (todos los usuarios)
const graphqlProxy = createProxyMiddleware({
    target: REPORTS_SERVICE_URL,
    changeOrigin: true,
    timeout: 10000,
    proxyTimeout: 10000,
    pathRewrite: {
        '^/api/graphql': '/api/graphql'
    },
    onProxyReq: (proxyReq, req, res) => {
        console.log(`[GraphQL Proxy] PROXY REQ: ${req.method} ${req.url} -> ${REPORTS_SERVICE_URL}/api/graphql`);
        
        // Fix content-length for JSON body
        if (req.body && req.method === 'POST') {
            const bodyData = JSON.stringify(req.body);
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
            proxyReq.write(bodyData);
            console.log(`[GraphQL Proxy] Body sent:`, bodyData);
        }
        
        // Add user headers
        if (req.user) {
            proxyReq.setHeader('X-User-ID', req.user.id);
            proxyReq.setHeader('X-User-Role', req.user.role);
            proxyReq.setHeader('X-User-Organization', req.user.organization);
            console.log(`[GraphQL Proxy] User headers added for user ${req.user.id}`);
        }
    },
    onProxyRes: (proxyRes, req, res) => {
        console.log(`[GraphQL Proxy] PROXY RES: ${proxyRes.statusCode} for ${req.url}`);
    },
    onError: (err, req, res) => {
        console.error('[GraphQL Proxy] ERROR:', err.message);
        if (!res.headersSent) {
            res.status(503).json({
                success: false,
                error: 'Reports service unavailable',
                message: err.message
            });
        }
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

// GraphQL - Manual proxy implementation
router.post('/graphql', async (req, res) => {
    console.log('[GRAPHQL ROUTE] POST /graphql HIT!');
    console.log('[GRAPHQL ROUTE] User:', req.user ? `${req.user.id} (${req.user.role})` : 'NO USER');
    console.log('[GRAPHQL ROUTE] Body:', JSON.stringify(req.body, null, 2));
    
    try {
        const axios = require('axios');
        
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': req.headers.authorization
        };
        
        if (req.user) {
            headers['X-User-ID'] = req.user.id;
            headers['X-User-Role'] = req.user.role;
            headers['X-User-Organization'] = req.user.organization;
        }
        
        console.log('[GRAPHQL ROUTE] Sending request to reports service...');
        
        const response = await axios.post(`${REPORTS_SERVICE_URL}/api/graphql`, req.body, {
            headers,
            timeout: 10000
        });
        
        console.log('[GRAPHQL ROUTE] Got response:', response.status);
        res.json(response.data);
        
    } catch (error) {
        console.error('[GRAPHQL ROUTE] Error:', error.message);
        res.status(500).json({
            errors: [{
                message: 'Internal server error',
                extensions: { code: 'INTERNAL_ERROR' }
            }]
        });
    }
});

router.use('/graphql', (req, res, next) => {
    console.log(`[GRAPHQL FALLBACK] ${req.method} /graphql - This should not be hit if POST works`);
    next();
}, graphqlProxy);

// Reportes REST - Solo PRESIDENTE y VOCAL para exportación Excel de donaciones
router.use('/reports', requireRole(['PRESIDENTE', 'VOCAL']), reportsProxy);

// Filtros - Todos los usuarios autenticados (el servicio maneja la lógica de permisos internamente)
router.use('/filters', filtersProxy);

// Consulta de red SOAP - Solo PRESIDENTES
router.use('/network', requireRole(['PRESIDENTE']), networkProxy);

module.exports = router;