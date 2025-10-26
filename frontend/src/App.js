import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import { AuthProvider } from './contexts/AuthContext';
import apolloClient from './config/apollo';
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
import DistributedDonationsHistoryPage from './pages/DistributedDonationsHistory';
import ExternalEvents from './pages/ExternalEvents';
import Network from './pages/Network';
import NotificationCenter from './components/notifications/NotificationCenter';
import DonationRequests from './pages/DonationRequests';
import DonationTransfers from './pages/DonationTransfers';
import DonationOffers from './pages/DonationOffers';
import AdhesionManagement from './pages/AdhesionManagement';
import Reports from './pages/Reports';
import NotFound from './pages/NotFound';

function App() {
  return (
    <ApolloProvider client={apolloClient}>
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

          {/* Notificaciones - Todos los roles */}
          <Route path="notifications" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO']}>
              <NotificationCenter />
            </RoleProtectedRoute>
          } />

          {/* Red de ONGs - PRESIDENTE, COORDINADOR, VOCAL y VOLUNTARIO */}
          <Route path="network" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO']}>
              <Network />
            </RoleProtectedRoute>
          } />

          {/* Eventos Externos - PRESIDENTE, COORDINADOR y VOLUNTARIO */}
          <Route path="external-events" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']}>
              <ExternalEvents />
            </RoleProtectedRoute>
          } />

          {/* Solicitudes de Donaciones - PRESIDENTE y VOCAL */}
          <Route path="donation-requests" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'VOCAL']}>
              <DonationRequests />
            </RoleProtectedRoute>
          } />

          {/* Transferencias de Donaciones - PRESIDENTE y VOCAL */}
          <Route path="donation-transfers" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'VOCAL']}>
              <DonationTransfers />
            </RoleProtectedRoute>
          } />

          {/* Ofertas de Donaciones - PRESIDENTE y VOCAL */}
          <Route path="donation-offers" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'VOCAL']}>
              <DonationOffers />
            </RoleProtectedRoute>
          } />

          {/* Gestión de Adhesiones - PRESIDENTE, COORDINADOR, VOCAL y VOLUNTARIO */}
          <Route path="adhesion-management" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO']}>
              <AdhesionManagement />
            </RoleProtectedRoute>
          } />

          {/* Reportes - Todos los roles */}
          <Route path="reports" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOCAL', 'VOLUNTARIO']}>
              <Reports />
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

          {/* Ver historial de donaciones repartidas - PRESIDENTE, COORDINADOR y VOLUNTARIO */}
          <Route path="events/:id/donations-history" element={
            <RoleProtectedRoute roles={['PRESIDENTE', 'COORDINADOR', 'VOLUNTARIO']}>
              <DistributedDonationsHistoryPage />
            </RoleProtectedRoute>
          } />
        </Route>

        {/* Ruta 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
    </ApolloProvider>
  );
}

export default App;