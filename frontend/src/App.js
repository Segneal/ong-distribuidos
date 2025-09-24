import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/common/Layout';
import ProtectedRoute, { RoleProtectedRoute, PermissionProtectedRoute } from './components/auth/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Users from './pages/Users';
import Inventory from './pages/Inventory';
import Events from './pages/Events';
import EventFormPage from './pages/EventForm';
import ParticipantManagerPage from './pages/ParticipantManager';
import DistributedDonationsPage from './pages/DistributedDonations';
import NotFound from './pages/NotFound';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Ruta pública de login */}
        <Route path="/login" element={<Login />} />
        
        {/* Rutas protegidas con layout */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          {/* Página de inicio - accesible para todos los usuarios autenticados */}
          <Route index element={<Home />} />
          
          {/* Gestión de usuarios - solo PRESIDENTE */}
          <Route path="users" element={
            <RoleProtectedRoute roles={['PRESIDENTE']}>
              <Users />
            </RoleProtectedRoute>
          } />
          
          {/* Inventario - PRESIDENTE y VOCAL */}
          <Route path="inventory" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'VOCAL']}>
              <Inventory />
            </RoleProtectedRoute>
          } />
          
          {/* Eventos - PRESIDENTE, COORDINADOR y VOLUNTARIO */}
          <Route path="events" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']}>
              <Events />
            </RoleProtectedRoute>
          } />
          
          {/* Crear evento - PRESIDENTE y COORDINADOR */}
          <Route path="events/new" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR']}>
              <EventFormPage />
            </RoleProtectedRoute>
          } />
          
          {/* Editar evento - PRESIDENTE y COORDINADOR */}
          <Route path="events/:id/edit" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR']}>
              <EventFormPage />
            </RoleProtectedRoute>
          } />
          
          {/* Gestión de participantes - PRESIDENTE y COORDINADOR */}
          <Route path="events/:id/participants" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR']}>
              <ParticipantManagerPage />
            </RoleProtectedRoute>
          } />
          
          {/* Registrar donaciones repartidas - PRESIDENTE y COORDINADOR */}
          <Route path="events/:id/donations" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR']}>
              <DistributedDonationsPage />
            </RoleProtectedRoute>
          } />
        </Route>
        
        {/* Ruta 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;