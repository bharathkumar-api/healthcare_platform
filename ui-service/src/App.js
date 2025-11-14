import React, { useState, useEffect } from 'react';
import Providers from './pages/Providers';
import './App.css';

const API_URL = 'http://localhost:8090';
const WS_URL = 'ws://localhost:8004';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [notifications, setNotifications] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch user on mount
  useEffect(() => {
    if (token && !user) {
      fetchUser();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        console.error('Failed to fetch user');
        if (response.status === 401) {
          logout();
        }
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  // WebSocket connection
  useEffect(() => {
    if (token && user) {
      const wsUrl = `${WS_URL}/ws/${user.id}`;
      console.log(`Attempting WebSocket connection to: ${wsUrl}`);
      
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          setWsConnected(true);
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('📨 Received notification:', data);
          setNotifications(prev => [data, ...prev]);
          
          if (Notification.permission === 'granted' && data.type !== 'connection') {
            new Notification(data.title || 'Healthcare Platform', {
              body: data.message,
              icon: '🏥'
            });
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);
        };
        
        return () => {
          ws.close();
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
      }
    }
  }, [token, user]);

  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const login = async (username, password) => {
    try {
      setLoading(true);
      setError('');
      
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        
        const userResponse = await fetch(`${API_URL}/api/v1/auth/me`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        const userData = await userResponse.json();
        setUser(userData);
        setLoading(false);
        return { success: true };
      } else {
        setLoading(false);
        return { success: false, error: data.detail };
      }
    } catch (error) {
      setLoading(false);
      return { success: false, error: error.message };
    }
  };

  const register = async (username, email, password, role) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          email,
          password,
          role: role || 'patient'
        })
      });

      const data = await response.json();
      setLoading(false);
      
      if (response.ok) {
        return { success: true, message: 'Registration successful! Please login.' };
      } else {
        return { success: false, error: data.detail || 'Registration failed' };
      }
    } catch (error) {
      setLoading(false);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    setToken('');
    setUser(null);
    setActiveTab('dashboard');
    localStorage.removeItem('token');
  };

  if (!token) {
    return <AuthPage onLogin={login} onRegister={register} />;
  }

  return (
    <div className="App">
      <Header 
        user={user} 
        onLogout={logout} 
        wsConnected={wsConnected}
        notificationCount={notifications.length}
      />
      
      <div className="container">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main className="main-content">
          {loading && <div className="loading">Loading...</div>}
          {error && <div className="error-message">{error}</div>}
          
          {activeTab === 'dashboard' && <Dashboard token={token} user={user} />}
          {activeTab === 'providers' && <Providers token={token} />}
          {activeTab === 'records' && <MedicalRecords token={token} />}
          {activeTab === 'notifications' && <NotificationsList token={token} />}
          {activeTab === 'profile' && <PatientProfile token={token} />}
          {activeTab === 'appointments' && <Appointments token={token} />}
        </main>
      </div>
    </div>
  );
}

function Header({ user, onLogout, wsConnected, notificationCount }) {
  return (
    <header className="header">
      <div className="header-content">
        <h1>🏥 Healthcare Platform</h1>
        <div className="header-right">
          <div className="ws-status">
            <span className={`status-dot ${wsConnected ? 'connected' : 'disconnected'}`}></span>
            {wsConnected ? 'Connected' : 'Disconnected'}
          </div>
          {notificationCount > 0 && (
            <div className="notification-badge">{notificationCount}</div>
          )}
          <span>Welcome, {user?.username || 'User'}</span>
          <button onClick={onLogout} className="btn-secondary">Logout</button>
        </div>
      </div>
    </header>
  );
}

function Sidebar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'profile', icon: '👤', label: 'My Profile' },
    { id: 'appointments', icon: '📅', label: 'Appointments' },
    { id: 'providers', icon: '🔍', label: 'Find Providers' },
    { id: 'notifications', icon: '🔔', label: 'Notifications' }
  ];

  return (
    <aside className="sidebar">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`sidebar-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => {
            console.log(`Switching to tab: ${tab.id}`);
            setActiveTab(tab.id);
          }}
        >
          <span className="icon">{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </aside>
  );
}

function AuthPage({ onLogin, onRegister }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('patient');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    if (isLogin) {
      const result = await onLogin(username, password);
      setLoading(false);
      if (!result.success) {
        setError(result.error || 'Login failed');
      }
    } else {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }
      
      if (password.length < 6) {
        setError('Password must be at least 6 characters');
        setLoading(false);
        return;
      }
      
      const result = await onRegister(username, email, password, role);
      setLoading(false);
      
      if (result.success) {
        setSuccess(result.message);
        setTimeout(() => {
          setIsLogin(true);
          setSuccess('');
          setPassword('');
          setConfirmPassword('');
        }, 2000);
      } else {
        setError(result.error || 'Registration failed');
      }
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccess('');
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="login-page">
      <div className="login-box">
        <h1>🏥 Healthcare Platform</h1>
        <h2>{isLogin ? 'Login' : 'Sign Up'}</h2>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>
          
          {!isLogin && (
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                required
              />
            </div>
          )}
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          
          {!isLogin && (
            <>
              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm password"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>I am a:</label>
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="patient">Patient</option>
                  <option value="doctor">Doctor</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </>
          )}
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Sign Up')}
          </button>
        </form>
        
        <div className="auth-switch">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button onClick={switchMode} className="link-button">
              {isLogin ? 'Sign Up' : 'Login'}
            </button>
          </p>
        </div>
        
        {isLogin && (
          <div className="demo-credentials">
            <p><strong>Demo Credentials:</strong></p>
            <p>Username: demo | Password: demo123</p>
            <button 
              className="btn-demo"
              onClick={() => {
                setUsername('demo');
                setPassword('demo123');
              }}
            >
              Use Demo Account
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Dashboard, PatientProfile, Appointments, Providers, NotificationsList components remain the same as before
// (Include all the component code from previous version)

function Dashboard({ token, user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      console.log('Fetching dashboard data...');
      
      const appointmentsRes = await fetch(`${API_URL}/api/v1/appointments/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const appointments = appointmentsRes.ok ? await appointmentsRes.json() : [];

      const profileRes = await fetch(`${API_URL}/api/v1/patients/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const profile = profileRes.ok ? await profileRes.json() : null;

      setStats({
        upcomingAppointments: appointments.filter(a => a.status === 'scheduled').length,
        totalAppointments: appointments.length,
        hasProfile: !!profile
      });
      
      console.log('Dashboard data loaded:', { appointments: appointments.length, hasProfile: !!profile });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-info">
            <h3>{stats?.upcomingAppointments || 0}</h3>
            <p>Upcoming Appointments</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-info">
            <h3>{stats?.totalAppointments || 0}</h3>
            <p>Total Appointments</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">👤</div>
          <div className="stat-info">
            <h3>{stats?.hasProfile ? 'Complete' : 'Incomplete'}</h3>
            <p>Profile Status</p>
          </div>
        </div>
      </div>

      <div className="welcome-section">
        <h3>Welcome back, {user?.username}! 👋</h3>
        <p>Manage your health records, book appointments, and stay connected with your healthcare providers.</p>
      </div>
    </div>
  );
}

function PatientProfile({ token }) {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      console.log('Fetching patient profile...');
      const response = await fetch(`${API_URL}/api/v1/patients/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Profile loaded:', data);
        setProfile(data);
        setFormData(data);
      } else {
        console.log('No profile found, ready to create');
        setProfile(null);
        setFormData({
          date_of_birth: '',
          gender: '',
          blood_type: '',
          phone: '',
          address: '',
          emergency_contact: '',
          emergency_phone: '',
          insurance_provider: '',
          insurance_number: ''
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async () => {
    try {
      console.log('Saving profile:', formData);
      const response = await fetch(`${API_URL}/api/v1/patients/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        await fetchProfile();
        setEditing(false);
        alert('Profile saved successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to save profile: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Failed to save profile');
    }
  };

  if (loading) return <div className="loading">Loading profile...</div>;

  return (
    <div className="patient-profile">
      <div className="profile-header">
        <h2>My Profile</h2>
        <div className="button-group">
          {profile && !editing && (
            <button className="btn-primary" onClick={() => setEditing(true)}>
              Edit Profile
            </button>
          )}
          {editing && (
            <>
              <button className="btn-primary" onClick={saveProfile}>
                Save Changes
              </button>
              <button className="btn-secondary" onClick={() => {
                setEditing(false);
                setFormData(profile || {});
              }}>
                Cancel
              </button>
            </>
          )}
          {!profile && !editing && (
            <button className="btn-primary" onClick={() => setEditing(true)}>
              Create Profile
            </button>
          )}
        </div>
      </div>

      {!editing && profile ? (
        <div className="profile-view">
          <div className="profile-section">
            <h3>Personal Information</h3>
            <p><strong>Date of Birth:</strong> {profile.date_of_birth}</p>
            <p><strong>Gender:</strong> {profile.gender}</p>
            <p><strong>Blood Type:</strong> {profile.blood_type}</p>
            <p><strong>Phone:</strong> {profile.phone}</p>
            <p><strong>Address:</strong> {profile.address}</p>
          </div>

          <div className="profile-section">
            <h3>Emergency Contact</h3>
            <p><strong>Name:</strong> {profile.emergency_contact}</p>
            <p><strong>Phone:</strong> {profile.emergency_phone}</p>
          </div>

          <div className="profile-section">
            <h3>Insurance</h3>
            <p><strong>Provider:</strong> {profile.insurance_provider}</p>
            <p><strong>Number:</strong> {profile.insurance_number}</p>
          </div>
        </div>
      ) : editing ? (
        <div className="profile-edit">
          <div className="form-row">
            <div className="form-group">
              <label>Date of Birth</label>
              <input
                type="date"
                value={formData.date_of_birth || ''}
                onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Gender</label>
              <select
                value={formData.gender || ''}
                onChange={(e) => setFormData({...formData, gender: e.target.value})}
              >
                <option value="">Select...</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label>Blood Type</label>
              <input
                type="text"
                value={formData.blood_type || ''}
                onChange={(e) => setFormData({...formData, blood_type: e.target.value})}
                placeholder="A+, B+, O+, etc."
              />
            </div>
          </div>

          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              value={formData.phone || ''}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              placeholder="+1-555-1234"
            />
          </div>

          <div className="form-group">
            <label>Address</label>
            <textarea
              value={formData.address || ''}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Emergency Contact Name</label>
              <input
                type="text"
                value={formData.emergency_contact || ''}
                onChange={(e) => setFormData({...formData, emergency_contact: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Emergency Contact Phone</label>
              <input
                type="tel"
                value={formData.emergency_phone || ''}
                onChange={(e) => setFormData({...formData, emergency_phone: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Insurance Provider</label>
              <input
                type="text"
                value={formData.insurance_provider || ''}
                onChange={(e) => setFormData({...formData, insurance_provider: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Insurance Number</label>
              <input
                type="text"
                value={formData.insurance_number || ''}
                onChange={(e) => setFormData({...formData, insurance_number: e.target.value})}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="no-profile">
          <p>No profile information available. Click "Create Profile" to get started.</p>
        </div>
      )}
    </div>
  );
}

function Appointments({ token }) {
  const [appointments, setAppointments] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [newAppointment, setNewAppointment] = useState({
    doctor_name: '',
    specialty: '',
    appointment_date: '',
    reason: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      console.log('Fetching appointments...');
      const response = await fetch(`${API_URL}/api/v1/appointments/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      console.log('Appointments loaded:', data.length);
      setAppointments(data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const bookAppointment = async () => {
    try {
      console.log('Booking appointment:', newAppointment);
      const response = await fetch(`${API_URL}/api/v1/appointments/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newAppointment,
          status: 'scheduled'
        })
      });

      if (response.ok) {
        await fetchAppointments();
        setShowForm(false);
        setNewAppointment({ doctor_name: '', specialty: '', appointment_date: '', reason: '' });
        alert('Appointment booked successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to book appointment: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert('Failed to book appointment');
    }
  };

  if (loading) return <div className="loading">Loading appointments...</div>;

  return (
    <div className="appointments">
      <div className="appointments-header">
        <h2>My Appointments</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Book Appointment'}
        </button>
      </div>

      {showForm && (
        <div className="appointment-form">
          <h3>Book New Appointment</h3>
          
          <div className="form-group">
            <label>Doctor Name</label>
            <input
              type="text"
              value={newAppointment.doctor_name}
              onChange={(e) => setNewAppointment({...newAppointment, doctor_name: e.target.value})}
              placeholder="Dr. John Smith"
            />
          </div>

          <div className="form-group">
            <label>Specialty</label>
            <select
              value={newAppointment.specialty}
              onChange={(e) => setNewAppointment({...newAppointment, specialty: e.target.value})}
            >
              <option value="">Select specialty...</option>
              <option value="Cardiology">Cardiology</option>
              <option value="Dermatology">Dermatology</option>
              <option value="Neurology">Neurology</option>
              <option value="Pediatrics">Pediatrics</option>
              <option value="Orthopedics">Orthopedics</option>
            </select>
          </div>

          <div className="form-group">
            <label>Date & Time</label>
            <input
              type="datetime-local"
              value={newAppointment.appointment_date}
              onChange={(e) => setNewAppointment({...newAppointment, appointment_date: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Reason for Visit</label>
            <textarea
              value={newAppointment.reason}
              onChange={(e) => setNewAppointment({...newAppointment, reason: e.target.value})}
              rows="3"
              placeholder="Describe your symptoms or reason for appointment..."
            />
          </div>

          <button className="btn-primary" onClick={bookAppointment}>
            Book Appointment
          </button>
        </div>
      )}

      <div className="appointments-list">
        {appointments.length === 0 ? (
          <p className="no-data">No appointments scheduled. Click "Book Appointment" to schedule one.</p>
        ) : (
          appointments.map((apt) => (
            <div key={apt.id} className="appointment-card">
              <div className="appointment-header">
                <h3>{apt.doctor_name}</h3>
                <span className={`status-badge ${apt.status}`}>
                  {apt.status}
                </span>
              </div>
              <p><strong>Specialty:</strong> {apt.specialty}</p>
              <p><strong>Date:</strong> {new Date(apt.appointment_date).toLocaleString()}</p>
              <p><strong>Reason:</strong> {apt.reason}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function NotificationsList({ notifications, token, user }) {
  const sendTestNotification = async () => {
    try {
      console.log('Sending test notification...');
      await fetch(`${API_URL}/api/v1/notifications/push`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          type: 'test',
          title: 'Test Notification',
          message: `Test sent at ${new Date().toLocaleTimeString()}`,
          data: { source: 'ui' }
        })
      });
      alert('Test notification sent! Check if it appears in real-time.');
    } catch (error) {
      console.error('Error sending test notification:', error);
      alert('Failed to send test notification');
    }
  };

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <h2>Notifications</h2>
        <button className="btn-primary" onClick={sendTestNotification}>
          Send Test Notification
        </button>
      </div>
      
      {notifications.length === 0 ? (
        <div className="no-data">
          <p>No notifications yet</p>
          <p>Click "Send Test Notification" to test real-time delivery</p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.map((notif, index) => (
            <div key={index} className="notification-item">
              <div className="notif-header">
                <strong>{notif.title}</strong>
                <small>{notif.timestamp ? new Date(notif.timestamp).toLocaleString() : 'Just now'}</small>
              </div>
              <p>{notif.message}</p>
              <span className="notif-type">{notif.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
