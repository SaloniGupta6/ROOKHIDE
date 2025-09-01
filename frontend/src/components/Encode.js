import React, { useState } from 'react';
import axios from 'axios';
import { getApiUrl, API_ENDPOINTS } from '../config';

const Encode = ({ walletAddress, sessionToken, walletConnected }) => {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('text');
  const [selfDestructTimer, setSelfDestructTimer] = useState('');
  const [customHeaders, setCustomHeaders] = useState({
    event: '',
    site: '',
    white: '',
    black: ''
  });
  const [loading, setLoading] = useState(false);
  const [, setTransactionId] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleHeaderChange = (field, value) => {
    setCustomHeaders(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const initiatePayment = async () => {
    console.log('🔥 Button clicked! Starting payment initiation...');
    console.log('Wallet connected:', walletConnected);
    console.log('Wallet address:', walletAddress);
    console.log('File selected:', file);
    
    // Double-check wallet connection
    if (!walletConnected || !walletAddress) {
      alert('❌ Coinbase Wallet must be connected first!');
      return;
    }

    if (!file) {
      alert('❌ Please select a file to encode');
      return;
    }

    console.log('✅ All checks passed, proceeding with payment...');

    try {
      setLoading(true);
      setPaymentStatus('🔄 Calculating file hash...');

      // Calculate file hash for X402 payment verification
      const fileData = await file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', fileData);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const fileHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

      setPaymentStatus('💰 Initiating X402 micropayment...');

      // Initiate X402 payment
      const response = await axios.post(getApiUrl(API_ENDPOINTS.PAYMENT_INITIATE), {
        wallet_address: walletAddress,
        operation: 'encode',
        file_hash: fileHash
      });

      if (response.data.success) {
        setTransactionId(response.data.transaction_id);
        setPaymentStatus(
          `💳 X402 Payment Required: ${response.data.payment_amount_eth} ETH\n` +
          `⏰ Payment expires in 15 minutes\n` +
          `🔄 Processing payment...`
        );
        
        // In production, this would trigger the actual wallet payment
        // For demo, we simulate the payment process
        setTimeout(() => {
          setPaymentStatus('✅ Simulating X402 payment completion...');
          setTimeout(() => {
            verifyPayment(response.data.transaction_id);
          }, 2000);
        }, 3000);
      }
    } catch (error) {
      console.error('🚨 X402 payment initiation error:', error);
      console.error('Error details:', error.response?.data);
      const errorMsg = error.response?.data?.message || error.message || 'X402 payment initiation failed';
      setPaymentStatus(`❌ ${errorMsg}`);
      alert(`❌ Error: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (txId) => {
    try {
      setPaymentStatus('Verifying payment...');
      
      // Simulate transaction hash (in production, this comes from the actual blockchain transaction)
      const simulatedTxHash = '0x' + Math.random().toString(16).substr(2, 64);
      
      const response = await axios.post(getApiUrl(API_ENDPOINTS.PAYMENT_VERIFY), {
        transaction_id: txId,
        tx_hash: simulatedTxHash
      });

      if (response.data.success) {
        setPaymentStatus('Payment verified! Processing encoding...');
        await processEncoding(txId);
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setPaymentStatus('Payment verification failed');
    }
  };

  const processEncoding = async (txId) => {
    try {
      console.log('🔄 Starting encoding process...');
      console.log('Transaction ID:', txId);
      console.log('File:', file);
      console.log('Wallet:', walletAddress);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', fileType);
      formData.append('wallet_address', walletAddress);
      formData.append('transaction_id', txId);
      
      if (selfDestructTimer) {
        formData.append('self_destruct_timer', selfDestructTimer);
      }

      // Add custom headers
      Object.entries(customHeaders).forEach(([key, value]) => {
        if (value) {
          formData.append(`pgn_${key}`, value);
        }
      });

      const response = await axios.post(getApiUrl(API_ENDPOINTS.ENCODE), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult(response.data);
        setPaymentStatus('Encoding completed successfully!');
      }
    } catch (error) {
      console.error('Encoding error:', error);
      setPaymentStatus('Encoding failed');
    }
  };

  const downloadResult = async () => {
    if (result && result.download_url) {
      window.open(`${getApiUrl('')}${result.download_url}`, '_blank');
    }
  };

  if (!walletConnected) {
    return (
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🔒</div>
          <h2 className="text-2xl font-semibold mb-4 text-red-600">Coinbase Wallet Required</h2>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-red-800 mb-2">Authentication Required</h3>
            <p className="text-red-700 mb-4">
              You must connect your Coinbase Wallet before encoding any files. This ensures:
            </p>
            <ul className="text-left text-red-700 space-y-2">
              <li>• Secure authentication and ownership verification</li>
              <li>• X402 micropayment processing for encoding services</li>
              <li>• Blockchain-based file metadata storage</li>
              <li>• Access to your previously encoded files</li>
            </ul>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800 text-sm">
              <strong>Next Steps:</strong> Connect wallet → Pay via X402 → Encode file
            </p>
          </div>
          <button 
            onClick={() => window.location.href = '/wallet'}
            className="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600 transition-colors"
          >
            Go to Wallet Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-semibold mb-6">Encode Secret Message</h2>
      
      <div className="space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File to Hide
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            accept=".txt,.png,.jpg,.jpeg"
          />
        </div>

        {/* File Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            File Type
          </label>
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="text">Text</option>
            <option value="image">Image</option>
          </select>
        </div>

        {/* Self-Destruct Timer */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Self-Destruct Timer (seconds, optional)
          </label>
          <input
            type="number"
            value={selfDestructTimer}
            onChange={(e) => setSelfDestructTimer(e.target.value)}
            placeholder="e.g., 3600 for 1 hour"
            className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Custom PGN Headers */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Chess Game Headers (optional)
          </label>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Event name"
              value={customHeaders.event}
              onChange={(e) => handleHeaderChange('event', e.target.value)}
              className="p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Site/Location"
              value={customHeaders.site}
              onChange={(e) => handleHeaderChange('site', e.target.value)}
              className="p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="White player"
              value={customHeaders.white}
              onChange={(e) => handleHeaderChange('white', e.target.value)}
              className="p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Black player"
              value={customHeaders.black}
              onChange={(e) => handleHeaderChange('black', e.target.value)}
              className="p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Payment Status */}
        {paymentStatus && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800">{paymentStatus}</p>
          </div>
        )}

        {/* Wallet Status */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✅</span>
            <span className="text-green-800 font-medium">Coinbase Wallet Connected</span>
          </div>
          <p className="text-green-700 text-sm mt-1">
            Address: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
          </p>
        </div>

        {/* Payment Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 mb-2">X402 Micropayment Required</h3>
          <div className="text-blue-700 text-sm space-y-1">
            <p>• Encoding fee: ~0.002 ETH (X402 protocol)</p>
            <p>• Payment processed via Coinbase Wallet</p>
            <p>• Secure blockchain verification</p>
            <p>• File metadata stored on-chain</p>
          </div>
        </div>

        {/* Test Button */}
        <button
          onClick={async () => {
            console.log('🧪 Test button clicked');
            try {
              const response = await axios.get(getApiUrl(API_ENDPOINTS.HEALTH));
              console.log('✅ Health check response:', response.data);
              alert('✅ Backend connection successful!');
            } catch (error) {
              console.error('❌ Health check failed:', error);
              alert('❌ Backend connection failed: ' + error.message);
            }
          }}
          className="w-full bg-yellow-500 text-white py-2 px-4 rounded-lg hover:bg-yellow-600 transition-colors mb-4"
        >
          🧪 Test Backend Connection
        </button>

        {/* Action Button */}
        <button
          onClick={initiatePayment}
          disabled={loading || !file || !walletConnected}
          className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-4 px-6 rounded-lg hover:from-green-600 hover:to-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing X402 Payment...
            </span>
          ) : (
            '🔐 Pay via X402 & Encode Message'
          )}
        </button>

        {/* Result */}
        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">Encoding Successful!</h3>
            <p className="text-green-700 mb-2">PGN ID: {result.pgn_id}</p>
            <p className="text-green-700 mb-4">File Hash: {result.pgn_hash}</p>
            <button
              onClick={downloadResult}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
            >
              Download Encoded PGN
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Encode;