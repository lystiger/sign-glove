import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { apiRequest } from '../api';

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const loginRes = await apiRequest('post', '/auth/login', { email, password });
      if (loginRes?.access_token) {
        localStorage.setItem('access_token', loginRes.access_token);
      }
      const me = await apiRequest('get', '/auth/me');
      onLogin(me);
      toast.success('Signed in');
    } catch (e) {
      toast.error(e.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-in" style={{ maxWidth: 400, margin: '2rem auto' }}>
      <h2>Sign In</h2>
      <form onSubmit={submit}>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
};

export default Login;