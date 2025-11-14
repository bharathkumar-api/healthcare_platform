import React, { useState, useEffect } from 'react';
function NotificationsList({ token }) {
  const [notifications, setNotifications] = useState([]);
  useEffect(() => {
    fetch('http://localhost:8090/api/v1/notifications/', { headers: { 'Authorization': `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : [])
      .then(data => setNotifications(data.notifications || []))
      .catch(err => console.error(err));
  }, [token]);
  return (
    <div style={{ padding: '20px' }}>
      <h2>🔔 Notifications</h2>
      {notifications.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', background: '#f9f9f9', borderRadius: '12px' }}>
          <p style={{ fontSize: '48px' }}>🔔</p>
          <h3>No notifications</h3>
          <p>You're all caught up!</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {notifications.map(n => (
            <div key={n.id} style={{ padding: '15px', background: 'white', border: '1px solid #ddd', borderRadius: '8px' }}>
              <h4>{n.title}</h4>
              <p>{n.message}</p>
              <small style={{ color: '#999' }}>{new Date(n.created_at).toLocaleString()}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
export default NotificationsList;
