import React from 'react';
import { useNavigate } from 'react-router-dom';

const Records = () => {
  const navigate = useNavigate();

  const mockRecords = [
    { id: 1, date: '2025-11-01', type: 'Lab Report', doctor: 'Dr. Smith', description: 'Blood Test Results' },
    { id: 2, date: '2025-10-15', type: 'Prescription', doctor: 'Dr. Johnson', description: 'Medication for flu' },
    { id: 3, date: '2025-09-20', type: 'X-Ray', doctor: 'Dr. Williams', description: 'Chest X-Ray' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 text-blue-600 hover:text-blue-800"
        >
          ← Back to Dashboard
        </button>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">📄 Medical Records</h1>

          <div className="space-y-4">
            {mockRecords.map((record) => (
              <div
                key={record.id}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-3">
                        {record.type === 'Lab Report' ? '🧪' : record.type === 'Prescription' ? '💊' : '📋'}
                      </span>
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{record.type}</h3>
                        <p className="text-sm text-gray-600">{record.date}</p>
                      </div>
                    </div>
                    <p className="text-gray-700 mt-2">
                      <strong>Doctor:</strong> {record.doctor}
                    </p>
                    <p className="text-gray-700 mt-1">
                      <strong>Description:</strong> {record.description}
                    </p>
                  </div>
                  <div className="flex flex-col space-y-2">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      View
                    </button>
                    <button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {mockRecords.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No medical records found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Records;
