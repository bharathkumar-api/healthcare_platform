import React, { useState, useEffect } from 'react';
import './Components.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function Billing({ token }) {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/billing/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBills(data);
      }
    } catch (error) {
      console.error('Error fetching bills:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="billing-page">
      <div className="page-header">
        <h1>💳 Billing & Payments</h1>
      </div>
      {message && <div className="alert">{message}</div>}
      <div className="bills-list">
        {loading ? (
          <div className="loading">Loading bills...</div>
        ) : bills.length > 0 ? (
          bills.map((bill) => (
            <div key={bill.id} className="bill-card">
              <h3>Bill #{bill.id}</h3>
              <p>Amount: ${bill.amount}</p>
              <p>Status: {bill.status}</p>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>💳 No bills found</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Billing;
