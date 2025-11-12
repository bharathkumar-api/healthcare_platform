import React, { useState, useEffect } from 'react';
import './Components.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function PatientProfile({ token, user }) {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    phone: '',
    address: '',
    date_of_birth: '',
    gender: '',
    blood_type: '',
    emergency_contact: ''
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/patients/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setFormData({
          phone: data.phone || '',
          address: data.address || '',
          date_of_birth: data.date_of_birth || '',
          gender: data.gender || '',
          blood_type: data.blood_type || '',
          emergency_contact: data.emergency_contact || ''
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_URL}/api/v1/patients/me`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setMessage('Profile updated successfully!');
        setEditing(false);
        fetchProfile();
      } else {
        setMessage('Failed to update profile');
      }
    } catch (error) {
      setMessage('Error updating profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !profile) {
    return <div className="loading">Loading profile...</div>;
  }

  return (
    <div className="profile-page">
      <div className="page-header">
        <h1>👤 My Profile</h1>
        <button className="btn-edit" onClick={() => setEditing(!editing)}>
          {editing ? '❌ Cancel' : '✏️ Edit Profile'}
        </button>
      </div>

      {message && <div className="alert">{message}</div>}

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user?.full_name?.charAt(0) || user?.username?.charAt(0) || '?'}
            </div>
            <h2>{user?.full_name || user?.username}</h2>
            <p>{user?.email}</p>
            <span className="role-badge">{user?.role}</span>
          </div>

          {!editing ? (
            <div className="profile-details">
              <div className="detail-item">
                <strong>📞 Phone:</strong>
                <span>{profile?.phone || 'Not set'}</span>
              </div>
              <div className="detail-item">
                <strong>📍 Address:</strong>
                <span>{profile?.address || 'Not set'}</span>
              </div>
              <div className="detail-item">
                <strong>🎂 Date of Birth:</strong>
                <span>{profile?.date_of_birth || 'Not set'}</span>
              </div>
              <div className="detail-item">
                <strong>⚧ Gender:</strong>
                <span>{profile?.gender || 'Not set'}</span>
              </div>
              <div className="detail-item">
                <strong>🩸 Blood Type:</strong>
                <span>{profile?.blood_type || 'Not set'}</span>
              </div>
              <div className="detail-item">
                <strong>🚨 Emergency Contact:</strong>
                <span>{profile?.emergency_contact || 'Not set'}</span>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="profile-form">
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+1 234 567 8900"
                />
              </div>

              <div className="form-group">
                <label>Address</label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="123 Main St, City, State, ZIP"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Date of Birth</label>
                <input
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Blood Type</label>
                <select
                  value={formData.blood_type}
                  onChange={(e) => setFormData({ ...formData, blood_type: e.target.value })}
                >
                  <option value="">Select Blood Type</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div className="form-group">
                <label>Emergency Contact</label>
                <input
                  type="text"
                  value={formData.emergency_contact}
                  onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
                  placeholder="Name: +1 234 567 8900"
                />
              </div>

              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Saving...' : '💾 Save Changes'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default PatientProfile;
