import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../components/network/Network.css';

const Network = () => {
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  const networkFeatures = [
    {
      title: 'Solicitudes de Donaciones',
      description: 'Publique solicitudes de donaciones y vea las necesidades de otras organizaciones',
      icon: '📋',
      path: '/donation-requests',
      permission: 'inventory',
      color: '#3498db'
    },
    {
      title: 'Transferencias',
      description: 'Transfiera donaciones directamente a organizaciones que las necesitan',
      icon: '🔄',
      path: '/donation-transfers',
      permission: 'inventory',
      color: '#e74c3c'
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
      title: 'Eventos Solidarios',
      description: 'Descubra eventos de otras organizaciones y permita adhesiones a los suyos',
      icon: '🤝',
      path: '/external-events',
      permission: 'events',
      color: '#9b59b6'
    }
  ];

  const handleFeatureClick = (feature) => {
    if (hasPermission(feature.permission, 'read')) {
      navigate(feature.path);
    }
  };

  return (
    <div className="network-page">
      <div className="page-header">
        <h1>Red de ONGs</h1>
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

      <div className="features-section">
        <h2>Funcionalidades de la Red</h2>
        <div className="features-grid">
          {networkFeatures.map((feature, index) => (
            <div
              key={index}
              className={`feature-card ${hasPermission(feature.permission, 'read') ? 'clickable' : 'disabled'}`}
              onClick={() => handleFeatureClick(feature)}
              style={{ borderLeftColor: feature.color }}
            >
              <div className="feature-icon" style={{ color: feature.color }}>
                {feature.icon}
              </div>
              <div className="feature-content">
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                {!hasPermission(feature.permission, 'read') && (
                  <div className="permission-notice">
                    Requiere permisos de {feature.permission === 'inventory' ? 'inventario' : 'eventos'}
                  </div>
                )}
              </div>
              {hasPermission(feature.permission, 'read') && (
                <div className="feature-arrow">→</div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="network-info">
        <div className="info-section">
          <h3>¿Cómo funciona la Red de ONGs?</h3>
          <div className="info-grid">
            <div className="info-item">
              <div className="info-number">1</div>
              <div className="info-content">
                <h4>Publique sus necesidades</h4>
                <p>Cree solicitudes de donaciones específicas que se compartirán con toda la red</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">2</div>
              <div className="info-content">
                <h4>Responda a solicitudes</h4>
                <p>Transfiera donaciones de su inventario a organizaciones que las necesiten</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">3</div>
              <div className="info-content">
                <h4>Comparta eventos</h4>
                <p>Publique eventos solidarios y permita que voluntarios de otras ONGs participen</p>
              </div>
            </div>
            <div className="info-item">
              <div className="info-number">4</div>
              <div className="info-content">
                <h4>Colabore efectivamente</h4>
                <p>Maximice el impacto social a través de la colaboración entre organizaciones</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="getting-started">
        <h3>Primeros Pasos</h3>
        <div className="steps-container">
          <div className="step-item">
            <div className="step-icon">📝</div>
            <div className="step-content">
              <h4>Configure su organización</h4>
              <p>Asegúrese de que su perfil organizacional esté completo</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">📦</div>
            <div className="step-content">
              <h4>Actualice su inventario</h4>
              <p>Mantenga actualizado su inventario para transferencias efectivas</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">🔗</div>
            <div className="step-content">
              <h4>Comience a colaborar</h4>
              <p>Explore solicitudes externas y publique las suyas propias</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Network;