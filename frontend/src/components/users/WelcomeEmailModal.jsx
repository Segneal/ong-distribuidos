import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Box,
  Typography
} from '@mui/material';
import { emailService } from '../../services/api';

const WelcomeEmailModal = ({ open, onClose, user }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [temporaryPassword, setTemporaryPassword] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');

  const generateRandomPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  };

  const handleGeneratePassword = () => {
    const newPassword = generateRandomPassword();
    setTemporaryPassword(newPassword);
  };

  const handleSendEmail = async () => {
    if (!temporaryPassword.trim()) {
      setError('Por favor genera o ingresa una contraseña temporal');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await emailService.sendWelcomeEmail({
        email: user.email,
        username: user.username,
        fullName: `${user.firstName} ${user.lastName}`,
        temporaryPassword: temporaryPassword.trim()
      });

      setSuccess(true);
      if (response.data.previewUrl) {
        setPreviewUrl(response.data.previewUrl);
      }
      
      setTimeout(() => {
        if (!response.data.previewUrl) {
          handleClose();
        }
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Error al enviar el email');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setTemporaryPassword('');
    setSuccess(false);
    setError('');
    setLoading(false);
    setPreviewUrl('');
    onClose();
  };

  if (!user) return null;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Enviar Email de Bienvenida
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body1" gutterBottom>
            <strong>Usuario:</strong> {user.firstName} {user.lastName}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Email:</strong> {user.email}
          </Typography>
        </Box>

        {success ? (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              ¡Email de bienvenida enviado correctamente! El usuario recibirá sus credenciales en su correo.
            </Alert>
            {previewUrl && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Vista previa del email (solo en desarrollo):
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => window.open(previewUrl, '_blank')}
                  sx={{ mb: 2 }}
                >
                  Ver Email Enviado
                </Button>
              </Box>
            )}
          </Box>
        ) : (
          <>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Contraseña Temporal"
                value={temporaryPassword}
                onChange={(e) => setTemporaryPassword(e.target.value)}
                placeholder="Ingresa una contraseña temporal o genera una automáticamente"
                disabled={loading}
                sx={{ mb: 1 }}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={handleGeneratePassword}
                disabled={loading}
              >
                Generar Automáticamente
              </Button>
            </Box>

            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Importante:</strong> Esta contraseña será enviada por email al usuario. 
                El usuario deberá cambiarla en su primer inicio de sesión.
              </Typography>
            </Alert>
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          {success ? 'Cerrar' : 'Cancelar'}
        </Button>
        {!success && (
          <Button
            onClick={handleSendEmail}
            variant="contained"
            disabled={loading || !temporaryPassword.trim()}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {loading ? 'Enviando...' : 'Enviar Email'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default WelcomeEmailModal;