import React, { useState } from 'react';
import axios from 'axios';

const LoginTest = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testDirectLogin = async () => {
    setLoading(true);
    setResult('Testing...');
    
    try {
      console.log('=== DIRECT LOGIN TEST ===');
      console.log('URL:', 'http://localhost:3001/api/auth/login');
      console.log('Data:', { usernameOrEmail: 'admin', password: 'admin123' });
      
      const response = await axios.post('http://localhost:3001/api/auth/login', {
        usernameOrEmail: 'admin',
        password: 'admin123'
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response:', response);
      setResult(`SUCCESS: ${JSON.stringify(response.data, null, 2)}`);
      
    } catch (error) {
      console.error('Error:', error);
      setResult(`ERROR: ${error.message}\nResponse: ${JSON.stringify(error.response?.data, null, 2)}\nStatus: ${error.response?.status}`);
    } finally {
      setLoading(false);
    }
  };

  const testWithAuthService = async () => {
    setLoading(true);
    setResult('Testing with auth service...');
    
    try {
      const { authService } = await import('../../services/api');
      console.log('=== AUTH SERVICE TEST ===');
      
      const response = await authService.login({
        usernameOrEmail: 'admin',
        password: 'admin123'
      });
      
      console.log('Auth service response:', response);
      setResult(`AUTH SERVICE SUCCESS: ${JSON.stringify(response.data, null, 2)}`);
      
    } catch (error) {
      console.error('Auth service error:', error);
      setResult(`AUTH SERVICE ERROR: ${error.message}\nResponse: ${JSON.stringify(error.response?.data, null, 2)}\nStatus: ${error.response?.status}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h2>Login Test</h2>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={testDirectLogin} disabled={loading} style={{ marginRight: '10px' }}>
          Test Direct Axios
        </button>
        <button onClick={testWithAuthService} disabled={loading}>
          Test Auth Service
        </button>
      </div>
      
      <div style={{ 
        background: '#f5f5f5', 
        padding: '10px', 
        border: '1px solid #ccc',
        whiteSpace: 'pre-wrap',
        maxHeight: '400px',
        overflow: 'auto'
      }}>
        {result || 'Click a button to test...'}
      </div>
    </div>
  );
};

export default LoginTest;