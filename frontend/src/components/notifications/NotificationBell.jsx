import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { IconButton, Badge, Menu, MenuItem, Typography, Divider, Box } from '@mui/material';
import { Notifications, NotificationsNone } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

const NotificationBell = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadNotifications();
      // Cargar notificaciones cada 30 segundos
      const interval = setInterval(loadNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/notifications');
      
      if (response.data.success) {
        const notifs = response.data.notifications || [];
        // Solo mostrar las últimas 5 notificaciones en el dropdown
        setNotifications(notifs.slice(0, 5));
        setUnreadCount(notifs.filter(n => !n.leida).length);
      }
    } catch (err) {
      console.error('Error loading notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notification) => {
    // Marcar como leída si no lo está
    if (!notification.leida) {
      try {
        await api.put(`/notifications/${notification.id}/read`);
        setUnreadCount(prev => Math.max(0, prev - 1));
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notification.id 
              ? { ...notif, leida: true }
              : notif
          )
        );
      } catch (err) {
        console.error('Error marking notification as read:', err);
      }
    }
    
    handleClose();
    // Navegar al centro de notificaciones
    navigate('/notifications');
  };

  const handleViewAll = () => {
    handleClose();
    navigate('/notifications');
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

  const formatDate = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Ahora';
    if (diffInMinutes < 60) return `${diffInMinutes}m`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h`;
    return `${Math.floor(diffInMinutes / 1440)}d`;
  };

  const truncateText = (text, maxLength = 50) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        sx={{ 
          color: 'white',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)'
          }
        }}
      >
        <Badge 
          badgeContent={unreadCount} 
          color="error"
          max={99}
        >
          {unreadCount > 0 ? <Notifications /> : <NotificationsNone />}
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 350,
            maxHeight: 400,
            mt: 1
          }
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Notificaciones
            {unreadCount > 0 && (
              <Badge 
                badgeContent={unreadCount} 
                color="error" 
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
        </Box>

        {loading ? (
          <MenuItem disabled>
            <Typography variant="body2" color="text.secondary">
              Cargando...
            </Typography>
          </MenuItem>
        ) : notifications.length === 0 ? (
          <MenuItem disabled>
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="body2" color="text.secondary">
                🔔 No tienes notificaciones
              </Typography>
            </Box>
          </MenuItem>
        ) : (
          notifications.map((notification, index) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              sx={{
                flexDirection: 'column',
                alignItems: 'flex-start',
                py: 1.5,
                borderLeft: !notification.leida ? '3px solid #1976d2' : '3px solid transparent',
                backgroundColor: !notification.leida ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
                '&:hover': {
                  backgroundColor: !notification.leida ? 'rgba(25, 118, 210, 0.08)' : 'rgba(0, 0, 0, 0.04)'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'flex-start', width: '100%', gap: 1 }}>
                <Typography sx={{ fontSize: '1.2em', flexShrink: 0 }}>
                  {getNotificationIcon(notification.tipo)}
                </Typography>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      fontWeight: !notification.leida ? 600 : 400,
                      mb: 0.5,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5
                    }}
                  >
                    {truncateText(notification.titulo, 35)}
                    {!notification.leida && (
                      <Box 
                        sx={{ 
                          width: 6, 
                          height: 6, 
                          borderRadius: '50%', 
                          backgroundColor: '#1976d2',
                          flexShrink: 0
                        }} 
                      />
                    )}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ mb: 0.5 }}
                  >
                    {truncateText(notification.mensaje, 45)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(notification.fecha_creacion)}
                  </Typography>
                </Box>
              </Box>
            </MenuItem>
          ))
        )}

        {notifications.length > 0 && (
          <>
            <Divider />
            <MenuItem 
              onClick={handleViewAll}
              sx={{ 
                justifyContent: 'center',
                py: 1.5,
                backgroundColor: 'rgba(25, 118, 210, 0.04)',
                '&:hover': {
                  backgroundColor: 'rgba(25, 118, 210, 0.08)'
                }
              }}
            >
              <Typography 
                variant="body2" 
                color="primary"
                sx={{ fontWeight: 600 }}
              >
                Ver todas las notificaciones
              </Typography>
            </MenuItem>
          </>
        )}
      </Menu>
    </>
  );
};

export default NotificationBell;