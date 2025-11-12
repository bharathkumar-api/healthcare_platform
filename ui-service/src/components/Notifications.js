import React, { useState, useEffect } from 'react';
import './Components.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function Notifications({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/notifications/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="notifications-page">
      <div className="page-header">
        <h1>🔔 Notifications</h1>
      </div>
      <div className="notifications-list">
        {loading ? (
          <div className="loading">Loading notifications...</div>
        ) : notifications.length > 0 ? (
          notifications.map((notif) => (
            <div key={notif.id} className="notification-card">
              <h3>{notif.title}</h3>
              <p>{notif.message}</p>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>🔔 No notifications</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Notifications;
