import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function Dashboard({ token, user }) {
  const [stats, setStats] = useState({
    appointments: 0,
    upcomingAppointments: 0,
    pendingBills: 0,
    notifications: 0
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const appointmentsRes = await fetch(`${API_URL}/api/v1/appointments/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (appointmentsRes.ok) {
        const appointments = await appointmentsRes.json();
        setRecentAppointments(appointments.slice(0, 5));
        setStats(prev => ({
          ...prev,
          appointments: appointments.length,
          upcomingAppointments: appointments.filter(a => a.status === 'scheduled').length
        }));
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.full_name || user?.username}! 👋</h1>
        <p>Here's what's happening with your health today</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-info">
            <h3>{stats.appointments}</h3>
            <p>Total Appointments</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-info">
            <h3>{stats.upcomingAppointments}</h3>
            <p>Upcoming</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💳</div>
          <div className="stat-info">
            <h3>{stats.pendingBills}</h3>
            <p>Pending Bills</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div className="stat-info">
            <h3>{stats.notifications}</h3>
            <p>Notifications</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="recent-section">
          <h2>Recent Appointments</h2>
          {recentAppointments.length > 0 ? (
            <div className="appointments-list">
              {recentAppointments.map((apt, index) => (
                <div key={index} className="appointment-item">
                  <div className="appointment-date">
                    <span className="day">{new Date(apt.appointment_date).getDate()}</span>
                    <span className="month">{new Date(apt.appointment_date).toLocaleString('default', { month: 'short' })}</span>
                  </div>
                  <div className="appointment-details">
                    <h4>Dr. {apt.doctor_name || 'TBD'}</h4>
                    <p>{apt.reason || 'General Checkup'}</p>
                    <span className={`status status-${apt.status}`}>{apt.status}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No appointments yet. Schedule your first appointment!</p>
          )}
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <button className="action-btn">📅 Book Appointment</button>
          <button className="action-btn">👤 Update Profile</button>
          <button className="action-btn">💳 View Bills</button>
          <button className="action-btn">📄 Medical Records</button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
