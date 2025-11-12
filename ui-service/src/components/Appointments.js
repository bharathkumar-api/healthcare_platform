import React, { useState, useEffect } from 'react';
import './Components.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function Appointments({ token, user }) {
  const [appointments, setAppointments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    doctor_name: '',
    appointment_date: '',
    appointment_time: '',
    reason: '',
    notes: ''
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/appointments/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAppointments(data);
      }
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const appointmentData = {
        doctor_name: formData.doctor_name,
        appointment_date: `${formData.appointment_date}T${formData.appointment_time}:00`,
        reason: formData.reason,
        notes: formData.notes,
        status: 'scheduled'
      };

      console.log('Sending appointment data:', appointmentData);

      const response = await fetch(`${API_URL}/api/v1/appointments/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(appointmentData)
      });

      const responseData = await response.json();
      console.log('Response:', responseData);

      if (response.ok) {
        setMessage('✅ Appointment booked successfully!');
        setShowForm(false);
        setFormData({
          doctor_name: '',
          appointment_date: '',
          appointment_time: '',
          reason: '',
          notes: ''
        });
        fetchAppointments();
      } else {
        setMessage(`❌ Failed to book appointment: ${responseData.detail || JSON.stringify(responseData)}`);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      setMessage(`❌ Error booking appointment: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const cancelAppointment = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/appointments/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        setMessage('✅ Appointment cancelled');
        fetchAppointments();
      }
    } catch (error) {
      setMessage('❌ Error cancelling appointment');
    }
  };

  return (
    <div className="appointments-page">
      <div className="page-header">
        <h1>📅 My Appointments</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? '❌ Cancel' : '➕ Book Appointment'}
        </button>
      </div>

      {message && <div className="alert">{message}</div>}

      {showForm && (
        <div className="appointment-form-card">
          <h2>Book New Appointment</h2>
          <form onSubmit={handleSubmit} className="appointment-form">
            <div className="form-group">
              <label>Doctor Name</label>
              <input
                type="text"
                value={formData.doctor_name}
                onChange={(e) => setFormData({ ...formData, doctor_name: e.target.value })}
                placeholder="Dr. John Smith"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  value={formData.appointment_date}
                  onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>

              <div className="form-group">
                <label>Time</label>
                <input
                  type="time"
                  value={formData.appointment_time}
                  onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Reason for Visit</label>
              <input
                type="text"
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="Annual checkup, Follow-up, etc."
                required
              />
            </div>

            <div className="form-group">
              <label>Additional Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Any symptoms, concerns, or questions..."
                rows="4"
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Booking...' : '📅 Book Appointment'}
            </button>
          </form>
        </div>
      )}

      <div className="appointments-list">
        {loading ? (
          <div className="loading">Loading appointments...</div>
        ) : appointments.length > 0 ? (
          appointments.map((apt) => (
            <div key={apt.id} className="appointment-card">
              <div className="appointment-header">
                <div>
                  <h3>Dr. {apt.doctor_name}</h3>
                  <p className="appointment-reason">{apt.reason}</p>
                </div>
                <span className={`status-badge status-${apt.status}`}>
                  {apt.status}
                </span>
              </div>

              <div className="appointment-body">
                <div className="appointment-info">
                  <span>📅 {new Date(apt.appointment_date).toLocaleDateString()}</span>
                  <span>⏰ {new Date(apt.appointment_date).toLocaleTimeString()}</span>
                </div>
                {apt.notes && (
                  <p className="appointment-notes">📝 {apt.notes}</p>
                )}
              </div>

              {apt.status === 'scheduled' && (
                <div className="appointment-actions">
                  <button className="btn-cancel" onClick={() => cancelAppointment(apt.id)}>
                    ❌ Cancel
                  </button>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>📅 No appointments yet</p>
            <button className="btn-primary" onClick={() => setShowForm(true)}>
              Book your first appointment
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Appointments;
