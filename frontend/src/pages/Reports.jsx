import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert
} from '@mui/material';
import '../components/reports/Reports.css';
import {
  Assessment,
  BarChart,
  CloudSync,
  TrendingUp
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import DonationReports from '../components/reports/DonationReports';
import EventReports from '../components/reports/EventReports';
import NetworkConsultation from '../components/reports/NetworkConsultation';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Reports = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);

  // Verificar permisos
  const canViewDonationReports = user?.role === 'PRESIDENTE' || user?.role === 'VOCAL';
  const canViewNetworkConsultation = user?.role === 'PRESIDENTE';

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Configurar tabs según permisos
  const tabs = [
    {
      label: 'Reportes de Eventos',
      icon: <BarChart />,
      show: true,
      description: 'Análisis de participación y estadísticas de eventos'
    }
  ];

  if (canViewDonationReports) {
    tabs.unshift({
      label: 'Reportes de Donaciones',
      icon: <Assessment />,
      show: true,
      description: 'Análisis y exportación de datos de donaciones'
    });
  }

  if (canViewNetworkConsultation) {
    tabs.push({
      label: 'Consulta de Red',
      icon: <CloudSync />,
      show: true,
      description: 'Consulta externa de datos de la red de ONGs'
    });
  }

  const visibleTabs = tabs.filter(tab => tab.show);

  return (
    <Box>
      



      {/* Contenido principal */}
      <Paper sx={{ width: '100%' }}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="reports tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            {visibleTabs.map((tab, index) => (
              <Tab
                key={index}
                icon={tab.icon}
                label={tab.label}
                id={`reports-tab-${index}`}
                aria-controls={`reports-tabpanel-${index}`}
                sx={{ minHeight: 72 }}
              />
            ))}
          </Tabs>
        </Box>
        {/* Tab Panels */}
        {visibleTabs.map((tab, index) => (
          <TabPanel key={index} value={tabValue} index={index}>
            {/* Descripción del tab */}
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                {tab.description}
              </Typography>
            </Alert>

            {/* Contenido según el tab */}
            {index === 0 && canViewDonationReports && (
              <DonationReports />
            )}
            {((index === 0 && !canViewDonationReports) || (index === 1 && canViewDonationReports)) && (
              <EventReports />
            )}
            {index === visibleTabs.length - 1 && canViewNetworkConsultation && (
              <NetworkConsultation />
            )}
          </TabPanel>
        ))}
      </Paper>
    </Box>
  );
};

export default Reports;