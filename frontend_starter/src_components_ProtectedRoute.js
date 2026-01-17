/**
 * Protected Route Component
 * Ensures only authenticated users can access protected pages
 */

import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ component: Component, isAuthenticated, ...rest }) {
  return isAuthenticated ? <Component {...rest} /> : <Navigate to="/login" />;
}

export default ProtectedRoute;
