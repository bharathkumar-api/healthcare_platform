import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    username: ''
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('http://localhost:8090/api/v1/auth/me', {
        headers: getAuthHeaders()
      });
      setUser(response.data);
      setFormData({
        full_name: response.data.full_name || '',
        email: response.data.email || '',
        username: response.data.username || ''
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      if (error.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    alert('Profile update feature coming soon!');
    setEditing(false);
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-xl">Loading...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">👤 My Profile</h1>
            <button
              onClick={() => setEditing(!editing)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {editing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          {editing ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100"
                />
              </div>
              <button
                type="submit"
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Changes
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="border-b pb-4">
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="text-lg font-medium">{user?.full_name}</p>
              </div>
              <div className="border-b pb-4">
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-lg font-medium">{user?.email}</p>
              </div>
              <div className="border-b pb-4">
                <p className="text-sm text-gray-600">Username</p>
                <p className="text-lg font-medium">{user?.username}</p>
              </div>
              <div className="border-b pb-4">
                <p className="text-sm text-gray-600">Role</p>
                <p className="text-lg font-medium capitalize">{user?.role}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
