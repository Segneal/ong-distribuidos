import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/api';

// Estados de autenticación
const AuthState = {
  LOADING: 'loading',
  AUTHENTICATED: 'authenticated',
  UNAUTHENTICATED: 'unauthenticated',
  ERROR: 'error'
};

// Acciones del reducer
const AuthActions = {
  SET_LOADING: 'SET_LOADING',
  SET_AUTHENTICATED: 'SET_AUTHENTICATED',
  SET_UNAUTHENTICATED: 'SET_UNAUTHENTICATED',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Estado inicial
const initialState = {
  status: AuthState.LOADING,
  user: null,
  token: null,
  error: null
};

// Reducer para manejar el estado de autenticación
const authReducer = (state, action) => {
  switch (action.type) {
    case AuthActions.SET_LOADING:
      return {
        ...state,
        status: AuthState.LOADING,
        error: null
      };

    case AuthActions.SET_AUTHENTICATED:
      return {
        ...state,
        status: AuthState.AUTHENTICATED,
        user: action.payload.user,
        token: action.payload.token,
        error: null
      };

    case AuthActions.SET_UNAUTHENTICATED:
      return {
        ...state,
        status: AuthState.UNAUTHENTICATED,
        user: null,
        token: null,
        error: null
      };

    case AuthActions.SET_ERROR:
      return {
        ...state,
        status: AuthState.ERROR,
        error: action.payload
      };

    case AuthActions.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};

// Crear el contexto
const AuthContext = createContext();

// Hook para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

// Provider del contexto
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Verificar token al cargar la aplicación
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('authToken');
      const userData = localStorage.getItem('userData');

      if (token && userData) {
        try {
          // Verificar si el token sigue siendo válido
          const response = await authService.verify({ token });

          if (response.data.valid) {
            dispatch({
              type: AuthActions.SET_AUTHENTICATED,
              payload: {
                user: JSON.parse(userData),
                token: token
              }
            });
          } else {
            // Token inválido, limpiar storage
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            dispatch({ type: AuthActions.SET_UNAUTHENTICATED });
          }
        } catch (error) {
          // Error al verificar token, limpiar storage
          localStorage.removeItem('authToken');
          localStorage.removeItem('userData');
          dispatch({ type: AuthActions.SET_UNAUTHENTICATED });
        }
      } else {
        dispatch({ type: AuthActions.SET_UNAUTHENTICATED });
      }
    };

    initializeAuth();
  }, []);

  // Función para hacer login
  const login = async (credentials) => {
    try {
      dispatch({ type: AuthActions.SET_LOADING });

      const response = await authService.login(credentials);

      if (response.data.success) {
        const { user, token } = response.data;

        // Guardar en localStorage
        localStorage.setItem('authToken', token);
        localStorage.setItem('userData', JSON.stringify(user));

        dispatch({
          type: AuthActions.SET_AUTHENTICATED,
          payload: { user, token }
        });

        return { success: true, user };
      } else {
        dispatch({
          type: AuthActions.SET_ERROR,
          payload: response.data.error || 'Error de autenticación'
        });
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Error de conexión';
      dispatch({
        type: AuthActions.SET_ERROR,
        payload: errorMessage
      });
      return { success: false, error: errorMessage };
    }
  };

  // Función para hacer logout
  const logout = async () => {
    try {
      // Intentar hacer logout en el servidor
      await authService.logout();
    } catch (error) {
      console.error('Error al hacer logout en el servidor:', error);
    } finally {
      // Limpiar storage local independientemente del resultado
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      dispatch({ type: AuthActions.SET_UNAUTHENTICATED });
    }
  };

  // Función para limpiar errores
  const clearError = () => {
    dispatch({ type: AuthActions.CLEAR_ERROR });
  };

  // Función para verificar si el usuario tiene un rol específico
  const hasRole = (role) => {
    return state.user?.role === role;
  };

  // Función para verificar si el usuario tiene uno de varios roles
  const hasAnyRole = (roles) => {
    return roles.includes(state.user?.role);
  };

  // Función para verificar permisos
  const hasPermission = (resource, action) => {
    if (!state.user) return false;

    const permissions = {
      PRESIDENTE: {
        users: ['create', 'read', 'update', 'delete'],
        inventory: ['create', 'read', 'update', 'delete'],
        events: ['create', 'read', 'update', 'delete']
      },
      VOCAL: {
        inventory: ['create', 'read', 'update', 'delete']
      },
      COORDINADOR: {
        events: ['create', 'read', 'update', 'delete']
      },
      VOLUNTARIO: {
        events: ['read', 'participate']
      }
    };

    const userPermissions = permissions[state.user.role];
    if (!userPermissions) return false;

    const resourcePermissions = userPermissions[resource];
    if (!resourcePermissions) return false;

    return resourcePermissions.includes(action);
  };

  const value = {
    // Estado
    ...state,
    isLoading: state.status === AuthState.LOADING,
    isAuthenticated: state.status === AuthState.AUTHENTICATED,
    isUnauthenticated: state.status === AuthState.UNAUTHENTICATED,
    hasError: state.status === AuthState.ERROR,

    // Funciones
    login,
    logout,
    clearError,
    hasRole,
    hasAnyRole,
    hasPermission
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;