import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8090';
const SPECIALTIES = [
  'Cardiology',
  'Dermatology',
  'Neurology',
  'Pediatrics',
  'Orthopedics',
  'Oncology',
  'Psychiatry'
];

function Providers({ token }) {
  const [providers, setProviders] = useState([]);
  const [specialty, setSpecialty] = useState('');
  const [availableOnly, setAvailableOnly] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const searchProviders = async () => {
    if (!token) return;
    setLoading(true);
    setError('');

    const params = new URLSearchParams();
    if (specialty) params.append('specialty', specialty);
    params.append('available_only', availableOnly ? 'true' : 'false');

    try {
      const response = await fetch(`${API_URL}/api/v1/providers${params.toString() ? `?${params.toString()}` : ''}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch providers (status ${response.status})`);
      }

      const result = await response.json();
      const providerList = Array.isArray(result) ? result : result?.providers || [];
      setProviders(providerList);
    } catch (err) {
      console.error('Error fetching providers:', err);
      setError(err.message || 'Unable to load providers');
      setProviders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchProviders();
  }, [token]);

  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ color: '#1E3A8A', marginBottom: '1rem' }}>🔍 Find Providers</h1>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem', alignItems: 'center' }}>
        <select
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
          style={{ padding: '10px', borderRadius: '8px', border: '1px solid #ccc', minWidth: '200px' }}
        >
          <option value="">All specialties</option>
          {SPECIALTIES.map((spec) => (
            <option key={spec} value={spec}>{spec}</option>
          ))}
        </select>

        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="checkbox"
            checked={availableOnly}
            onChange={(e) => setAvailableOnly(e.target.checked)}
          />
          Available only
        </label>

        <button
          onClick={searchProviders}
          style={{
            padding: '10px 16px',
            backgroundColor: '#2563EB',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
          disabled={loading}
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '12px', background: '#FEE2E2', color: '#B91C1C', borderRadius: '8px', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ padding: '20px' }}><h2>Loading providers...</h2></div>
      ) : providers.length === 0 ? (
        <div style={{ padding: '20px', border: '1px dashed #94A3B8', borderRadius: '10px', color: '#475569' }}>
          No providers match this filter. Try a different specialty or include unavailable providers.
        </div>
      ) : (
        providers.map((provider) => (
          <div
            key={provider.id}
            style={{
              border: '1px solid #E5E7EB',
              padding: '20px',
              margin: '15px 0',
              borderRadius: '12px',
              background: '#F8FAFC',
              boxShadow: '0 2px 6px rgba(15, 23, 42, 0.05)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h2 style={{ margin: 0, color: '#0F172A' }}>{provider.name}</h2>
              {provider.available && (
                <span style={{ background: '#DCFCE7', color: '#166534', padding: '4px 10px', borderRadius: '999px', fontSize: '0.85rem' }}>
                  Available
                </span>
              )}
            </div>
            <p style={{ margin: '4px 0' }}><strong>Specialty:</strong> {provider.specialty}</p>
            <p style={{ margin: '4px 0' }}><strong>Qualification:</strong> {provider.qualification}</p>
            <p style={{ margin: '4px 0' }}><strong>Experience:</strong> {provider.experience_years} years</p>
            <p style={{ margin: '4px 0' }}><strong>Rating:</strong> ⭐ {provider.rating?.toFixed(1) || 'N/A'}</p>
            <p style={{ margin: '4px 0' }}><strong>Consultation fee:</strong> ${provider.consultation_fee}</p>
            <p style={{ margin: '4px 0' }}><strong>Phone:</strong> {provider.phone}</p>
            <p style={{ margin: '4px 0' }}><strong>Email:</strong> {provider.email}</p>
            <p style={{ margin: '4px 0', color: '#475569' }}>{provider.address}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default Providers;
