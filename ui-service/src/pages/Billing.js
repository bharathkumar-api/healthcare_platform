import React from 'react';
import { useNavigate } from 'react-router-dom';

const Billing = () => {
  const navigate = useNavigate();

  const mockBills = [
    { id: 1, date: '2025-11-01', description: 'General Checkup', amount: 150, status: 'Paid' },
    { id: 2, date: '2025-10-15', description: 'Blood Test', amount: 75, status: 'Paid' },
    { id: 3, date: '2025-09-20', description: 'X-Ray', amount: 200, status: 'Pending' },
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
          <h1 className="text-3xl font-bold text-gray-900 mb-6">💳 Billing & Payments</h1>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {mockBills.map((bill) => (
                  <tr key={bill.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {bill.date}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {bill.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${bill.amount}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          bill.status === 'Paid'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {bill.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {bill.status === 'Pending' ? (
                        <button className="text-blue-600 hover:text-blue-800">
                          Pay Now
                        </button>
                      ) : (
                        <button className="text-gray-600 hover:text-gray-800">
                          View Receipt
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Billing;
