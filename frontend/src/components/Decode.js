import React, { useState } from 'react';
import axios from 'axios';
import { getApiUrl, API_ENDPOINTS } from '../config';

const Decode = ({ walletAddress, sessionToken, walletConnected }) => {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState('text');
  const [loading, setLoading] = useState(false);
  const [, setTransactionId] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  const [result, setResult] = useState(null);
  const [pgnValidation, setPgnValidation] = useState(null);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    
    if (selectedFile && selectedFile.name.endsWith('.pgn')) {
      await validatePgn(selectedFile);
    }
  };

  const validatePgn = async (pgnFile) => {
    try {
      const formData = new FormData();
      formData.append('file', pgnFile);
      
      const response = await axios.post(getApiUrl(API_ENDPOINTS.PGN_VALIDATE), formData);
      
      if (response.data.success) {
        setPgnValidation(response.data);
      }
    } catch (error) {
      console.error('PGN validation error:', error);
    }
  };

  const initiatePayment = async () => {
    // Double-check wallet connection
    if (!walletConnected || !walletAddress) {
      alert('❌ Coinbase Wallet must be connected first!');
      return;
    }

    if (!file) {
      alert('❌ Please select a PGN file to decode');
      return;
    }

    if (!file.name.endsWith('.pgn')) {
      alert('❌ Please select a valid PGN file');
      return;
    }

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
        operation: 'decode',
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
      console.error('X402 payment initiation error:', error);
      const errorMsg = error.response?.data?.message || 'X402 payment initiation failed';
      setPaymentStatus(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (txId) => {
    try {
      setPaymentStatus('🔍 Verifying X402 payment...');
      
      // Simulate transaction hash (in production, this comes from the actual blockchain transaction)
      const simulatedTxHash = '0x' + Math.random().toString(16).substr(2, 64);
      
      const response = await axios.post(getApiUrl(API_ENDPOINTS.PAYMENT_VERIFY), {
        transaction_id: txId,
        tx_hash: simulatedTxHash
      });

      if (response.data.success) {
        setPaymentStatus('✅ Payment verified! Processing decoding...');
        await processDecoding(txId);
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setPaymentStatus('❌ Payment verification failed');
    }
  };

  const processDecoding = async (txId) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', fileType);
      formData.append('wallet_address', walletAddress);
      formData.append('transaction_id', txId);

      const response = await axios.post(getApiUrl(API_ENDPOINTS.DECODE), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Important for file download
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `decoded_message.${fileType === 'text' ? 'txt' : 'png'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setPaymentStatus('🎉 Decoding completed successfully! File downloaded.');
      setResult({ success: true, message: 'Hidden message extracted and downloaded' });
    } catch (error) {
      console.error('Decoding error:', error);
      setPaymentStatus('❌ Decoding failed');
    }
  };

  if (!walletConnected) {
    return (
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🔓</div>
          <h2 className="text-2xl font-semibold mb-4 text-red-600">Coinbase Wallet Required</h2>
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-red-800 mb-2">Authentication Required</h3>
            <p className="text-red-700 mb-4">
              You must connect your Coinbase Wallet before decoding any files. This ensures:
            </p>
            <ul className="text-left text-red-700 space-y-2">
              <li>• Secure authentication and ownership verification</li>
              <li>• X402 micropayment processing for decoding services</li>
              <li>• Access to blockchain-verified PGN files</li>
              <li>• Protection against unauthorized access</li>
            </ul>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800 text-sm">
              <strong>Next Steps:</strong> Connect wallet → Pay via X402 → Decode PGN
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
      <h2 className="text-2xl font-semibold mb-6">Decode Hidden Message</h2>
      
      <div className="space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select PGN File to Decode
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            accept=".pgn"
          />
          <p className="text-sm text-gray-500 mt-1">
            Only PGN (Portable Game Notation) files are accepted
          </p>
        </div>

        {/* PGN Validation Results */}
        {pgnValidation && (
          <div className={`border rounded-lg p-4 ${
            pgnValidation.has_hidden_data 
              ? 'bg-green-50 border-green-200' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <h3 className="font-semibold mb-2">
              {pgnValidation.has_hidden_data ? '✅ Hidden Data Detected' : '⚠️ PGN Analysis'}
            </h3>
            <div className="text-sm space-y-1">
              <p>Valid PGN: {pgnValidation.is_valid_pgn ? '✅ Yes' : '❌ No'}</p>
              <p>Contains Hidden Data: {pgnValidation.has_hidden_data ? '✅ Yes' : '❌ No'}</p>
              <p>File Hash: <code className="bg-gray-100 px-1 rounded">{pgnValidation.file_hash.slice(0, 16)}...</code></p>
              {pgnValidation.pgn_exists_in_store && (
                <p className="text-green-600">🔗 File found in blockchain storage</p>
              )}
            </div>
          </div>
        )}

        {/* Expected Output Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expected Hidden Content Type
          </label>
          <select
            value={fileType}
            onChange={(e) => setFileType(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="text">Text File</option>
            <option value="image">Image File</option>
          </select>
        </div>

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
            <p>• Decoding fee: ~0.001 ETH (X402 protocol)</p>
            <p>• Payment processed via Coinbase Wallet</p>
            <p>• Secure blockchain verification</p>
            <p>• Access to hidden message content</p>
          </div>
        </div>

        {/* Payment Status */}
        {paymentStatus && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <pre className="text-blue-800 whitespace-pre-line text-sm">{paymentStatus}</pre>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={initiatePayment}
          disabled={loading || !file || !walletConnected || !pgnValidation?.has_hidden_data}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-4 px-6 rounded-lg hover:from-blue-600 hover:to-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold"
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
            '🔓 Pay via X402 & Decode Message'
          )}
        </button>

        {/* Result */}
        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">🎉 Decoding Successful!</h3>
            <p className="text-green-700">{result.message}</p>
          </div>
        )}

        {/* Help Text */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-2">How Decoding Works</h3>
          <div className="text-gray-600 text-sm space-y-1">
            <p>1. Upload a PGN file that contains hidden data</p>
            <p>2. Connect your Coinbase Wallet for authentication</p>
            <p>3. Pay the X402 micropayment for decoding service</p>
            <p>4. The hidden message is extracted from chess moves</p>
            <p>5. Download your decoded file automatically</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Decode;