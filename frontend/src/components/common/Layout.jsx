import React, { useState } from 'react';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  useTheme,
  useMediaQuery,
  Avatar,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountCircle,
  Logout,
  People,
  Inventory,
  Event,
  Home,
  Dashboard,
  RequestPage,
  SwapHoriz,
  LocalOffer,
  Hub,
  Notifications
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import NotificationBell from '../notifications/NotificationBell';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const { user, logout, hasPermission } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  // Manejar apertura/cierre del drawer móvil
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Manejar menú de usuario
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // Manejar logout
  const handleLogout = async () => {
    handleClose();
    await logout();
    navigate('/login');
  };

  // Navegación según rol
  const getNavigationItems = () => {
    const organizationItems = [
      {
        text: 'Inicio',
        icon: <Home />,
        path: '/',
        show: true
      }
    ];

    const networkItems = [];

    // Módulos de la Organización
    if (hasPermission('users', 'read')) {
      organizationItems.push({
        text: 'Usuarios',
        icon: <People />,
        path: '/users',
        show: true
      });
    }

    if (hasPermission('inventory', 'read')) {
      organizationItems.push({
        text: 'Inventario',
        icon: <Inventory />,
        path: '/inventory',
        show: true
      });
    }

    if (hasPermission('events', 'read')) {
      organizationItems.push({
        text: 'Eventos',
        icon: <Event />,
        path: '/events',
        show: true
      });
    }

    // Notificaciones - disponible para todos los usuarios autenticados
    organizationItems.push({
      text: 'Notificaciones',
      icon: <Notifications />,
      path: '/notifications',
      show: true
    });

    // Módulos de Red Interorganizacional
    networkItems.push({
      text: 'Red de ONGs',
      icon: <Hub />,
      path: '/network',
      show: true
    });

    if (hasPermission('events', 'read')) {
      networkItems.push({
        text: 'Eventos Externos',
        icon: <Dashboard />,
        path: '/external-events',
        show: true
      });
      networkItems.push({
        text: 'Gestión Adhesiones',
        icon: <People />,
        path: '/adhesion-management',
        show: true
      });
    }

    if (hasPermission('inventory', 'read')) {
      networkItems.push({
        text: 'Solicitudes Red',
        icon: <RequestPage />,
        path: '/donation-requests',
        show: true
      });
      networkItems.push({
        text: 'Transferencias',
        icon: <SwapHoriz />,
        path: '/donation-transfers',
        show: true
      });
      networkItems.push({
        text: 'Ofertas Red',
        icon: <LocalOffer />,
        path: '/donation-offers',
        show: true
      });
    }

    return {
      organization: organizationItems.filter(item => item.show),
      network: networkItems.filter(item => item.show)
    };
  };

  // Obtener color del chip según el rol
  const getRoleColor = (role) => {
    const colors = {
      PRESIDENTE: 'error',
      VOCAL: 'warning',
      COORDINADOR: 'info',
      VOLUNTARIO: 'success'
    };
    return colors[role] || 'default';
  };

  // Contenido del drawer
  const drawerContent = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Avatar sx={{ mx: 'auto', mb: 1, bgcolor: 'primary.main' }}>
          <AccountCircle />
        </Avatar>
        <Typography variant="subtitle1" noWrap>
          {user?.firstName} {user?.lastName}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          @{user?.username}
        </Typography>
        <Chip
          label={user?.role}
          size="small"
          color={getRoleColor(user?.role)}
          sx={{ mt: 1 }}
        />
      </Box>

      <Divider />

      {/* Módulos de la Organización */}
      <Box sx={{ px: 2, py: 1, backgroundColor: '#f5f5f5', borderRadius: 1, mx: 1, mb: 1 }}>
        <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#666' }}>
          🏢 ORGANIZACIÓN
        </Typography>
      </Box>
      <List>
        {getNavigationItems().organization.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) {
                  setMobileOpen(false);
                }
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider sx={{ my: 2 }} />

      {/* Módulos de Red Interorganizacional */}
      <Box sx={{ px: 2, py: 1, backgroundColor: '#e3f2fd', borderRadius: 1, mx: 1, mb: 1 }}>
        <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
          🌐 RED INTERORGANIZACIONAL
        </Typography>
      </Box>
      <List>
        {getNavigationItems().network.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) {
                  setMobileOpen(false);
                }
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${mobileOpen ? 250 : 0}px)` },
          ml: { md: `${mobileOpen ? 250 : 0}px` },
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            ONG Empuje Comunitario
          </Typography>

          {/* Menú de usuario en desktop */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
            <Chip
              label={user?.role}
              size="small"
              color={getRoleColor(user?.role)}
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />

            {/* Campanita de notificaciones */}
            <NotificationBell />

            <Button
              color="inherit"
              startIcon={<AccountCircle />}
              onClick={handleMenu}
            >
              {user?.firstName}
            </Button>

            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>
                <ListItemIcon>
                  <AccountCircle fontSize="small" />
                </ListItemIcon>
                <ListItemText>
                  {user?.firstName} {user?.lastName}
                </ListItemText>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" />
                </ListItemIcon>
                <ListItemText>Cerrar Sesión</ListItemText>
              </MenuItem>
            </Menu>
          </Box>

          {/* Notificaciones y logout en móvil */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', gap: 1 }}>
            <NotificationBell />
            <IconButton
              color="inherit"
              onClick={handleLogout}
            >
              <Logout />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: 250 }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'persistent'}
          open={isMobile ? mobileOpen : true}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: 250,
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Contenido principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - 250px)` },
          mt: '64px', // Height of AppBar
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;