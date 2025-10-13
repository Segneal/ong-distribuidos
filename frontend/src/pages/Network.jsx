import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../components/network/Network.css';

const Network = () => {
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  // Sección de Donaciones
  const donationFeatures = [
    {
      title: 'Solicitudes de Donaciones',
      description: 'Publique solicitudes de donaciones y vea las necesidades de otras organizaciones',
      icon: '📋',
      path: '/donation-requests',
      permission: 'inventory',
      color: '#3498db'
    },
    {
      title: 'Ofertas de Donaciones',
      description: 'Publique donaciones disponibles y explore ofertas de otras ONGs',
      icon: '🎁',
      path: '/donation-offers',
      permission: 'inventory',
      color: '#f39c12'
    },
    {
      title: 'Transferencias',
      description: 'Transfiera donaciones directamente a organizaciones que las necesitan',
      icon: '🔄',
      path: '/donation-transfers',
      permission: 'inventory',
      color: '#e74c3c'
    }
  ];

  // Sección de Eventos
  const eventFeatures = [
    {
      title: 'Eventos Solidarios',
      description: 'Descubra eventos de otras organizaciones y permita adhesiones a los suyos',
      icon: '🤝',
      path: '/external-events',
      permission: 'events',
      color: '#9b59b6'
    },
    {
      title: 'Gestión de Adhesiones',
      description: 'Administre las adhesiones a sus eventos y vea sus participaciones externas',
      icon: '👥',
      path: '/adhesion-management',
      permission: 'events',
      color: '#2ecc71'
    }
  ];

  const handleFeatureClick = (feature) => {
    if (hasPermission(feature.permission, 'read')) {
      navigate(feature.path);
    }
  };

  const renderFeatureCard = (feature) => (
    <div
      key={feature.path}
      className={`feature-card ${hasPermission(feature.permission, 'read') ? 'clickable' : 'disabled'}`}
      onClick={() => handleFeatureClick(feature)}
      style={{ borderLeftColor: feature.color }}
    >
      <div className="feature-icon">{feature.icon}</div>
      <div className="feature-content">
        <h3>{feature.title}</h3>
        <p>{feature.description}</p>
        {!hasPermission(feature.permission, 'read') && (
          <div className="permission-notice">
            Sin permisos para acceder a esta función
          </div>
        )}
      </div>
      {hasPermission(feature.permission, 'read') && (
        <div className="feature-arrow">→</div>
      )}
    </div>
  );

  return (
    <div className="network-page">
      <div className="page-header">
        <h1>Red Interorganizacional</h1>
        <p>Conecte con otras organizaciones para maximizar el impacto social</p>
      </div>

      <div className="network-stats">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">🌐</div>
            <div className="stat-content">
              <h3>Red Colaborativa</h3>
              <p>Conectado con organizaciones de toda la región</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🤲</div>
            <div className="stat-content">
              <h3>Donaciones Compartidas</h3>
              <p>Optimice la distribución de recursos</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <h3>Voluntarios Unidos</h3>
              <p>Amplíe el alcance de sus eventos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sección de Gestión de Donaciones */}
      <div className="features-section">
        <h2>🎁 Gestión de Donaciones</h2>
        <div className="features-grid">
          {donationFeatures.map(renderFeatureCard)}
        </div>
      </div>

      {/* Sección de Eventos Colaborativos */}
      <div className="features-section">
        <h2>🤝 Eventos Colaborativos</h2>
        <div className="features-grid">
          {eventFeatures.map(renderFeatureCard)}
        </div>
      </div>

      {/* Información sobre la Red */}
      <div className="network-info">
        <div className="info-section">
          <h3>¿Cómo funciona la Red Interorganizacional?</h3>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-number">1</div>
              <div className="info-content">
                <h4>Publique sus necesidades</h4>
                <p>Cree solicitudes de donaciones específicas que otras organizaciones puedan ver y responder</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">2</div>
              <div className="info-content">
                <h4>Comparta sus recursos</h4>
                <p>Ofrezca donaciones disponibles para que otras ONGs puedan solicitarlas</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">3</div>
              <div className="info-content">
                <h4>Colabore en eventos</h4>
                <p>Participe en eventos de otras organizaciones y permita que se adhieran a los suyos</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">4</div>
              <div className="info-content">
                <h4>Transfiera recursos</h4>
                <p>Realice transferencias directas de donaciones a organizaciones que las necesiten</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Guía de inicio rápido */}
      <div className="getting-started">
        <h3>Comience a colaborar</h3>
        <div className="steps-container">
          <div className="step-item">
            <div className="step-icon">📝</div>
            <div className="step-content">
              <h4>Crear solicitud</h4>
              <p>Publique qué donaciones necesita su organización</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">👀</div>
            <div className="step-content">
              <h4>Explorar ofertas</h4>
              <p>Vea qué recursos están disponibles en la red</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">🤝</div>
            <div className="step-content">
              <h4>Conectar</h4>
              <p>Participe en eventos y colabore con otras ONGs</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Network;