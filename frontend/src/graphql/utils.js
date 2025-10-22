// GraphQL utility functions

/**
 * Extracts error messages from Apollo GraphQL errors
 * @param {Object} error - Apollo error object
 * @returns {string} - Formatted error message
 */
export const getGraphQLErrorMessage = (error) => {
  if (!error) return 'Error desconocido';
  
  // Check for GraphQL errors
  if (error.graphQLErrors && error.graphQLErrors.length > 0) {
    return error.graphQLErrors[0].message;
  }
  
  // Check for network errors
  if (error.networkError) {
    if (error.networkError.statusCode === 401) {
      return 'No autorizado. Por favor, inicia sesión nuevamente.';
    }
    if (error.networkError.statusCode === 403) {
      return 'No tienes permisos para realizar esta acción.';
    }
    return `Error de red: ${error.networkError.message}`;
  }
  
  // Fallback to general message
  return error.message || 'Error desconocido';
};

/**
 * Checks if an error is due to authentication issues
 * @param {Object} error - Apollo error object
 * @returns {boolean} - True if it's an auth error
 */
export const isAuthError = (error) => {
  if (!error) return false;
  
  if (error.networkError && [401, 403].includes(error.networkError.statusCode)) {
    return true;
  }
  
  if (error.graphQLErrors) {
    return error.graphQLErrors.some(err => 
      err.extensions && 
      (err.extensions.code === 'UNAUTHENTICATED' || err.extensions.code === 'FORBIDDEN')
    );
  }
  
  return false;
};

/**
 * Default variables for GraphQL queries to handle undefined values
 * @param {Object} variables - Query variables
 * @returns {Object} - Cleaned variables object
 */
export const cleanGraphQLVariables = (variables) => {
  const cleaned = {};
  
  Object.keys(variables).forEach(key => {
    const value = variables[key];
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = value;
    }
  });
  
  return cleaned;
};