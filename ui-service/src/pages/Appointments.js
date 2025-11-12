import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Appointments = () => {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  
  const [formData, setFormData] = useState({
    doctor_name: '',
    appointment_date: '',
    appointment_time: '',
    reason: '',
    notes: '',
    status: 'scheduled'
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return null;
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const fetchAppointments = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;
      
      const response = await axios.get('http://localhost:8090/api/v1/appointments/', {
        headers
      });
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const dateTime = `${formData.appointment_date}T${formData.appointment_time}:00`;
      
      const appointmentData = {
        doctor_name: formData.doctor_name,
        appointment_date: dateTime,
        reason: formData.reason,
        notes: formData.notes,
        status: formData.status
      };

      await axios.post('http://localhost:8090/api/v1/appointments/', appointmentData, {
        headers
      });

      setSuccess('Appointment booked successfully!');
      setFormData({
        doctor_name: '',
        appointment_date: '',
        appointment_time: '',
        reason: '',
        notes: '',
        status: 'scheduled'
      });
      setShowForm(false);
      fetchAppointments();
    } catch (error) {
      console.error('Booking error:', error);
      if (error.response?.status === 401) {
        setError('Session expired. Please login again.');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError(error.response?.data?.detail || 'Failed to book appointment');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      await axios.delete(`http://localhost:8090/api/v1/appointments/${id}`, {
        headers
      });
      setSuccess('Appointment cancelled successfully');
      fetchAppointments();
    } catch (error) {
      setError('Failed to cancel appointment');
    }
  };

  const formatDateTime = (dateTimeStr) => {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">📅 My Appointments</h1>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-2 text-blue-600 hover:text-blue-800"
            >
              ← Back to Dashboard
            </button>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showForm ? '✕ Cancel' : '📅 Book New Appointment'}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            ❌ {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
            ✓ {success}
          </div>
        )}

        {showForm && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6">Book New Appointment</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Doctor Name
                </label>
                <input
                  type="text"
                  value={formData.doctor_name}
                  onChange={(e) => setFormData({ ...formData, doctor_name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                  <input
                    type="date"
                    value={formData.appointment_date}
                    onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Time</label>
                  <input
                    type="time"
                    value={formData.appointment_time}
                    onChange={(e) => setFormData({ ...formData, appointment_time: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Visit
                </label>
                <input
                  type="text"
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {loading ? '⏳ Booking...' : '📅 Book Appointment'}
              </button>
            </form>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-6">Your Appointments</h2>
          {appointments.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">📅 No appointments yet</p>
              <button
                onClick={() => setShowForm(true)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Book your first appointment
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {appointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">
                        Dr. {appointment.doctor_name}
                      </h3>
                      <p className="text-gray-600 mt-2">
                        📅 {formatDateTime(appointment.appointment_date)}
                      </p>
                      <p className="text-gray-600 mt-1">
                        📋 {appointment.reason}
                      </p>
                      {appointment.notes && (
                        <p className="text-gray-500 mt-2 text-sm">
                          📝 {appointment.notes}
                        </p>
                      )}
                      <span
                        className={`inline-block mt-3 px-3 py-1 rounded-full text-sm font-medium ${
                          appointment.status === 'scheduled'
                            ? 'bg-blue-100 text-blue-800'
                            : appointment.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {appointment.status}
                      </span>
                    </div>
                    <button
                      onClick={() => handleDelete(appointment.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Appointments;
