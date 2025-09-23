import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Tabs, 
  Tab, 
  Paper 
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  Inventory as InventoryIcon,
  Event as EventIcon,
  Login as LoginIcon
} from '@mui/icons-material';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleChange = (event, newValue) => {
    navigate(newValue);
  };

  // TODO: Implementar lógica de roles cuando se implemente autenticación
  const menuItems = [
    { label: 'Inicio', value: '/', icon: <HomeIcon /> },
    { label: 'Login', value: '/login', icon: <LoginIcon /> },
    { label: 'Usuarios', value: '/users', icon: <PeopleIcon /> },
    { label: 'Inventario', value: '/inventory', icon: <InventoryIcon /> },
    { label: 'Eventos', value: '/events', icon: <EventIcon /> },
  ];

  return (
    <Paper elevation={1}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs 
          value={location.pathname} 
          onChange={handleChange}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
        >
          {menuItems.map((item) => (
            <Tab
              key={item.value}
              label={item.label}
              value={item.value}
              icon={item.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Box>
    </Paper>
  );
};

export default Navigation;