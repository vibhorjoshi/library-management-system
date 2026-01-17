import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Analytics Dashboard Component
 * Displays fine statistics, payment trends, and book analytics
 */
const AnalyticsDashboard = ({ token, isAdmin }) => {
  const [analytics, setAnalytics] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        
        if (isAdmin) {
          // Fetch system analytics for admins
          const response = await axios.get(
            `${API_BASE_URL}/analytics/system/?days=${days}`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          setAnalytics(response.data);
        } else {
          // Fetch user analytics for regular users
          const response = await axios.get(
            `${API_BASE_URL}/analytics/user/`,
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );
          setUserAnalytics(response.data);
        }
        
        setError(null);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load analytics');
        console.error('Analytics error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [token, isAdmin, days]);

  if (loading) {
    return (
      <div className="analytics-container">
        <p className="text-center text-muted">Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        <h4>Error Loading Analytics</h4>
        <p>{error}</p>
      </div>
    );
  }

  // ADMIN VIEW: System Analytics
  if (isAdmin && analytics) {
    const { fine_statistics, payment_trends, overdue_analytics, revenue_analytics, top_defaulters, top_books } = analytics;

    return (
      <div className="analytics-container p-4">
        <h2 className="mb-4">📊 System Analytics Dashboard</h2>

        {/* Period Selection */}
        <div className="mb-4">
          <label className="form-label">Select Period:</label>
          <select
            className="form-select"
            value={days}
            onChange={(e) => setDays(e.target.value)}
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>

        {/* Fine Statistics Cards */}
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Total Fines</h5>
                <p className="card-text display-6">₹{fine_statistics.total_amount.toFixed(2)}</p>
                <small className="text-muted">{fine_statistics.total_fines} fines</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Paid Amount</h5>
                <p className="card-text display-6">₹{fine_statistics.paid_amount.toFixed(2)}</p>
                <small className="text-muted">{fine_statistics.paid_count} payments</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Pending Amount</h5>
                <p className="card-text display-6">₹{fine_statistics.pending_amount.toFixed(2)}</p>
                <small className="text-muted">{fine_statistics.unpaid_count} outstanding</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Average Fine</h5>
                <p className="card-text display-6">₹{fine_statistics.avg_fine_amount.toFixed(2)}</p>
                <small className="text-muted">Per fine</small>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Trends Chart */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">📈 Payment Trends</h5>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={payment_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke="#007bff"
                  name="Payment Amount (₹)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fine Distribution Pie Chart */}
        <div className="row mb-4">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Fine Status Distribution</h5>
              </div>
              <div className="card-body">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Paid', value: fine_statistics.paid_count },
                        { name: 'Unpaid', value: fine_statistics.unpaid_count },
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      <Cell fill="#28a745" />
                      <Cell fill="#dc3545" />
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Overdue Books Analytics */}
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Overdue Books</h5>
              </div>
              <div className="card-body">
                <p>
                  <strong>Total Overdue:</strong> {overdue_analytics.total_overdue}
                </p>
                <p>
                  <strong>Affected Users:</strong> {overdue_analytics.overdue_users}
                </p>
                <p>
                  <strong>Fine Amount:</strong> ₹{overdue_analytics.total_overdue_fine.toFixed(2)}
                </p>
                <hr />
                <h6>Overdue by Duration:</h6>
                <ul className="small">
                  <li>1-7 days: {overdue_analytics.books_by_days_overdue['1-7_days']}</li>
                  <li>8-14 days: {overdue_analytics.books_by_days_overdue['8-14_days']}</li>
                  <li>15-30 days: {overdue_analytics.books_by_days_overdue['15-30_days']}</li>
                  <li>Over 30 days: {overdue_analytics.books_by_days_overdue['over_30_days']}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Top Defaulters Table */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">⚠️ Top Defaulters</h5>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Unpaid Fines</th>
                    <th>Amount (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {top_defaulters.map((defaulter) => (
                    <tr key={defaulter.user_id}>
                      <td>{defaulter.username}</td>
                      <td>{defaulter.email}</td>
                      <td>{defaulter.unpaid_fines}</td>
                      <td className="text-danger">
                        ₹{defaulter.unpaid_amount.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Top Books Table */}
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">📚 Most Issued Books</h5>
          </div>
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-sm">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Times Issued</th>
                    <th>Currently Issued</th>
                    <th>Overdue</th>
                  </tr>
                </thead>
                <tbody>
                  {top_books.map((book) => (
                    <tr key={book.book_id}>
                      <td>{book.title}</td>
                      <td>{book.author}</td>
                      <td>{book.times_issued}</td>
                      <td>{book.currently_issued}</td>
                      <td>
                        <span className={`badge bg-${book.currently_overdue > 0 ? 'danger' : 'success'}`}>
                          {book.currently_overdue}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // USER VIEW: Personal Analytics
  if (!isAdmin && userAnalytics) {
    const { fine_statistics, overdue_books, pending_fines } = userAnalytics;

    return (
      <div className="analytics-container p-4">
        <h2 className="mb-4">📊 My Analytics</h2>

        {/* Personal Statistics Cards */}
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Total Fines</h5>
                <p className="card-text display-6">{fine_statistics.total_fines}</p>
                <small className="text-muted">₹{fine_statistics.total_amount.toFixed(2)}</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Paid</h5>
                <p className="card-text display-6 text-success">{fine_statistics.paid_count}</p>
                <small className="text-muted">₹{fine_statistics.paid_amount.toFixed(2)}</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Unpaid</h5>
                <p className="card-text display-6 text-danger">{fine_statistics.unpaid_count}</p>
                <small className="text-muted">₹{fine_statistics.pending_amount.toFixed(2)}</small>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Overdue Books</h5>
                <p className="card-text display-6 text-warning">{overdue_books}</p>
                <small className="text-muted">Currently due</small>
              </div>
            </div>
          </div>
        </div>

        {/* Fine Status Distribution */}
        <div className="card mb-4">
          <div className="card-header">
            <h5 className="mb-0">Fine Status</h5>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Paid', value: fine_statistics.paid_count },
                    { name: 'Unpaid', value: fine_statistics.unpaid_count },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill="#28a745" />
                  <Cell fill="#dc3545" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pending Fines List */}
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">⚠️ Pending Fines</h5>
          </div>
          <div className="card-body">
            {pending_fines.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-sm">
                  <thead>
                    <tr>
                      <th>Book</th>
                      <th>Amount (₹)</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pending_fines.map((fine) => (
                      <tr key={fine.id}>
                        <td>{fine.issued_book__book__title || 'N/A'}</td>
                        <td className="text-danger">₹{fine.amount.toFixed(2)}</td>
                        <td>{new Date(fine.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted">No pending fines. Great job!</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return <div>No analytics data available</div>;
};

export default AnalyticsDashboard;
