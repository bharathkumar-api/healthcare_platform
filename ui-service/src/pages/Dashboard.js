import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

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

  useEffect(() => {
    fetchUserData();
    fetchUpcomingAppointments();
  }, []);

  const fetchUserData = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await axios.get('http://localhost:8090/api/v1/auth/me', { headers });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchUpcomingAppointments = async () => {
    try {
      const headers = getAuthHeaders();
      if (!headers) return;

      const response = await axios.get('http://localhost:8090/api/v1/appointments/', { headers });
      setAppointments(response.data.slice(0, 3));
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">🏥 HealthCare</h1>
            <p className="text-gray-600 mt-1">Welcome back, {user?.full_name || user?.username}!</p>
            <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {user?.role}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            🚪 Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/appointments')}
              className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-2">📅</div>
              <div className="text-xl font-semibold">Book Appointment</div>
            </button>

            <button
              onClick={() => navigate('/profile')}
              className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-2">👤</div>
              <div className="text-xl font-semibold">Update Profile</div>
            </button>

            <button
              onClick={() => navigate('/billing')}
              className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-2">💳</div>
              <div className="text-xl font-semibold">View Bills</div>
            </button>

            <button
              onClick={() => navigate('/records')}
              className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-2">📄</div>
              <div className="text-xl font-semibold">Medical Records</div>
            </button>
          </div>
        </div>

        {/* Upcoming Appointments */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Upcoming Appointments</h2>
            <button
              onClick={() => navigate('/appointments')}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              View All →
            </button>
          </div>

          {appointments.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No upcoming appointments</p>
              <button
                onClick={() => navigate('/appointments')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Book an Appointment
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {appointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-lg">Dr. {appointment.doctor_name}</h3>
                      <p className="text-gray-600 mt-1">
                        📅 {new Date(appointment.appointment_date).toLocaleString()}
                      </p>
                      <p className="text-gray-600">📋 {appointment.reason}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        appointment.status === 'scheduled'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {appointment.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
