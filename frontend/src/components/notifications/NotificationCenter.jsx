import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Notifications.css';

const NotificationCenter = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (user) {
      loadNotifications();
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/notifications');
      
      if (response.data.success) {
        const notifs = response.data.notifications || [];
        setNotifications(notifs);
        setUnreadCount(notifs.filter(n => !n.leida).length);
      } else {
        setError('Error al cargar notificaciones');
      }
    } catch (err) {
      setError('Error al cargar notificaciones');
      console.error('Error loading notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/read`);
      
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId 
            ? { ...notif, leida: true, fecha_leida: new Date().toISOString() }
            : notif
        )
      );
      
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      
      setNotifications(prev => 
        prev.map(notif => ({ 
          ...notif, 
          leida: true, 
          fecha_leida: new Date().toISOString() 
        }))
      );
      
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'EVENT_CANCELLED':
        return '❌';
      case 'EVENT_UPDATED':
        return '📅';
      case 'DONATION_RECEIVED':
        return '🎁';
      default:
        return '📢';
    }
  };

  const getNotificationClass = (type) => {
    switch (type) {
      case 'EVENT_CANCELLED':
        return 'notification-error';
      case 'EVENT_UPDATED':
        return 'notification-warning';
      case 'DONATION_RECEIVED':
        return 'notification-success';
      default:
        return 'notification-info';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="notifications-container">
        <div className="loading">Cargando notificaciones...</div>
      </div>
    );
  }

  return (
    <div className="notifications-container">
      <div className="notifications-header">
        <h3>
          Notificaciones 
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </h3>
        {unreadCount > 0 && (
          <button 
            className="btn btn-secondary btn-sm"
            onClick={markAllAsRead}
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="notifications-list">
        {notifications.length === 0 ? (
          <div className="no-notifications">
            <span className="no-notifications-icon">🔔</span>
            <p>No tienes notificaciones</p>
          </div>
        ) : (
          notifications.map(notification => (
            <div 
              key={notification.id}
              className={`notification-item ${getNotificationClass(notification.tipo)} ${
                !notification.leida ? 'unread' : 'read'
              }`}
              onClick={() => !notification.leida && markAsRead(notification.id)}
            >
              <div className="notification-icon">
                {getNotificationIcon(notification.tipo)}
              </div>
              
              <div className="notification-content">
                <div className="notification-title">
                  {notification.titulo}
                  {!notification.leida && <span className="unread-dot">●</span>}
                </div>
                <div className="notification-message">
                  {notification.mensaje}
                </div>
                <div className="notification-date">
                  {formatDate(notification.fecha_creacion)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NotificationCenter;