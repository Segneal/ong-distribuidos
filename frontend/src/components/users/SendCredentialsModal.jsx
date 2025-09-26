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

const SendCredentialsModal = ({ open, onClose, user }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [password, setPassword] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');

  const generateRandomPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let newPassword = '';
    for (let i = 0; i < 8; i++) {
      newPassword += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return newPassword;
  };

  const handleGeneratePassword = () => {
    const newPassword = generateRandomPassword();
    setPassword(newPassword);
  };

  const handleSendCredentials = async () => {
    if (!password.trim()) {
      setError('Por favor genera o ingresa una contraseña');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await emailService.sendWelcomeEmail({
        email: user.email,
        username: user.username,
        temporaryPassword: password.trim(),
        fullName: `${user.firstName} ${user.lastName}`
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
      setError(err.response?.data?.message || 'Error al enviar las credenciales');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setPassword('');
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
          <Typography variant="body2" color="text.secondary">
            <strong>Username:</strong> {user.username}
          </Typography>
        </Box>

        {success ? (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              ¡Email de bienvenida enviado correctamente! El usuario recibirá sus credenciales por email.
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
                label="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingresa una contraseña o genera una automáticamente"
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
                <strong>Importante:</strong> Se enviará un email de bienvenida con las credenciales de acceso.
                Esta contraseña es temporal y el usuario deberá cambiarla en su primer inicio de sesión.
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
            onClick={handleSendCredentials}
            variant="contained"
            disabled={loading || !password.trim()}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {loading ? 'Enviando...' : 'Enviar Email'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SendCredentialsModal;