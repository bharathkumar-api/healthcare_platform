import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8090/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      }
    };
    fetchUser();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name || 'User'}!
          </h1>
          <p className="text-gray-600">Manage your healthcare all in one place</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/appointments')}
              className="flex items-center p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <span className="text-4xl mr-4">📅</span>
              <span className="text-xl font-semibold">Book Appointment</span>
            </button>

            <button
              onClick={() => navigate('/profile')}
              className="flex items-center p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <span className="text-4xl mr-4">👤</span>
              <span className="text-xl font-semibold">Update Profile</span>
            </button>

            <button
              onClick={() => navigate('/billing')}
              className="flex items-center p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <span className="text-4xl mr-4">💳</span>
              <span className="text-xl font-semibold">View Bills</span>
            </button>

            <button
              onClick={() => navigate('/records')}
              className="flex items-center p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
            >
              <span className="text-4xl mr-4">��</span>
              <span className="text-xl font-semibold">Medical Records</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
