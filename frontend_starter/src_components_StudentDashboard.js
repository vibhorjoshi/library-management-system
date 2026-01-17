/**
 * Student Dashboard Component
 * Shows student's issued books and reservations
 */

import React, { useState, useEffect } from 'react';
import { dashboardAPI, bookAPI } from '../services/api';
import 'bootstrap/dist/css/bootstrap.min.css';

function StudentDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await dashboardAPI.getDashboard();
      setDashboardData(response.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="row mb-4">
        <div className="col-md-12">
          <h1>Student Dashboard</h1>
          <p className="text-muted">
            Welcome, {dashboardData?.full_name}!
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h5 className="card-title">Books Issued</h5>
              <p className="card-text display-6">
                {dashboardData?.issued_books_count || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-info text-white">
            <div className="card-body">
              <h5 className="card-title">Reservations</h5>
              <p className="card-text display-6">
                {dashboardData?.reservations_count || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <h5 className="card-title">Pending Fines</h5>
              <p className="card-text display-6">
                Rs. {dashboardData?.pending_fines || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="mb-0">My Books & Information</h5>
            </div>
            <div className="card-body">
              <p>Complete book management and details would go here.</p>
              <p>This is a starter template - expand with your specific components.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StudentDashboard;
