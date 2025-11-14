import React, { useState } from 'react';
function MedicalRecords({ token }) {
  const [activeTab, setActiveTab] = useState('records');
  return (
    <div style={{ padding: '20px' }}>
      <h2>�� Medical Records</h2>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {['records', 'allergies', 'medications'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={{ padding: '10px 20px', background: activeTab === tab ? '#667eea' : '#f5f5f5', color: activeTab === tab ? 'white' : '#333', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>{tab.charAt(0).toUpperCase() + tab.slice(1)}</button>
        ))}
      </div>
      <div style={{ padding: '40px', textAlign: 'center', background: '#f9f9f9', borderRadius: '12px' }}>
        <p style={{ fontSize: '48px' }}>📄</p>
        <h3>No {activeTab} found</h3>
        <p>This feature is coming soon!</p>
      </div>
    </div>
  );
}
export default MedicalRecords;
