import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getApiUrl, API_ENDPOINTS } from '../config';

const WalletConnect = ({ walletConnected, walletAddress, onConnect, onDisconnect }) => {
  const [userFiles, setUserFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUserFiles = useCallback(async () => {
    if (!walletAddress) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${getApiUrl(API_ENDPOINTS.PGN_LIST)}?wallet_address=${walletAddress}`);
      if (response.data.success) {
        setUserFiles(response.data.pgns);
      }
    } catch (error) {
      console.error('Error fetching user files:', error);
      setError('Failed to fetch user files');
    } finally {
      setLoading(false);
    }
  }, [walletAddress]);

  useEffect(() => {
    if (walletConnected && walletAddress) {
      fetchUserFiles();
    }
  }, [walletConnected, walletAddress, fetchUserFiles]);

  const downloadFile = async (pgnId) => {
    try {
      window.open(`${getApiUrl(API_ENDPOINTS.DOWNLOAD)}/${pgnId}`, '_blank');
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getFileTypeIcon = (fileType) => {
    switch (fileType) {
      case 'text':
        return '📄';
      case 'image':
        return '🖼️';
      default:
        return '📁';
    }
  };

  if (!walletConnected) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="text-8xl mb-6">🔗</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">Connect Your Coinbase Wallet</h1>
            <p className="text-xl text-gray-600 mb-8">
              Secure access to the Chess Steganography DApp
            </p>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-6">
                <div className="text-3xl mb-3">🔐</div>
                <h3 className="font-semibold text-blue-800 mb-2">Secure Authentication</h3>
                <p className="text-blue-700 text-sm">
                  Cryptographically verified wallet signatures ensure your identity and ownership
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-6">
                <div className="text-3xl mb-3">💰</div>
                <h3 className="font-semibold text-green-800 mb-2">X402 Micropayments</h3>
                <p className="text-green-700 text-sm">
                  Small blockchain payments for encoding/decoding services via X402 protocol
                </p>
              </div>

              <div className="bg-purple-50 rounded-lg p-6">
                <div className="text-3xl mb-3">🗃️</div>
                <h3 className="font-semibold text-purple-800 mb-2">File Management</h3>
                <p className="text-purple-700 text-sm">
                  Access your encoded PGN files and manage your chess steganography history
                </p>
              </div>
            </div>

            <button
              onClick={onConnect}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg px-8 py-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg"
            >
              🔗 Connect Coinbase Wallet
            </button>

            <div className="mt-8 bg-gray-50 rounded-lg p-6">
              <h3 className="font-semibold text-gray-800 mb-4">What happens when you connect?</h3>
              <div className="text-left text-gray-600 space-y-2">
                <div className="flex items-start space-x-3">
                  <span className="text-green-500 font-bold">1.</span>
                  <span>Your Coinbase Wallet will prompt you to sign a verification message</span>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-500 font-bold">2.</span>
                  <span>We verify your wallet signature to authenticate your identity</span>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-500 font-bold">3.</span>
                  <span>You gain access to encode/decode features and file management</span>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-500 font-bold">4.</span>
                  <span>All operations are secured with X402 micropayments</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Wallet Dashboard</h1>
            <p className="text-gray-600">Manage your chess steganography files and wallet connection</p>
          </div>
          <div className="text-right">
            <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg mb-2">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="font-semibold">Connected</span>
              </div>
            </div>
            <p className="text-sm text-gray-600 font-mono">
              {walletAddress}
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-2xl font-bold text-blue-800">{userFiles.length}</div>
            <div className="text-sm text-blue-600">Total Files</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl mb-2">📄</div>
            <div className="text-2xl font-bold text-green-800">
              {userFiles.filter(f => f.file_type === 'text').length}
            </div>
            <div className="text-sm text-green-600">Text Files</div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl mb-2">🖼️</div>
            <div className="text-2xl font-bold text-purple-800">
              {userFiles.filter(f => f.file_type === 'image').length}
            </div>
            <div className="text-sm text-purple-600">Image Files</div>
          </div>

          <div className="bg-red-50 rounded-lg p-4">
            <div className="text-2xl mb-2">🔐</div>
            <div className="text-2xl font-bold text-red-800">
              {userFiles.length > 0 ? '✓' : '○'}
            </div>
            <div className="text-sm text-red-600">Active Wallet</div>
          </div>
        </div>

        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Your Encoded Files</h2>
          <button
            onClick={onDisconnect}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
          >
            Disconnect Wallet
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p>Loading your files...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-800">{error}</p>
            <button
              onClick={fetchUserFiles}
              className="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : userFiles.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="text-6xl mb-4">📂</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No files yet</h3>
            <p className="text-gray-600 mb-6">
              You haven't encoded any files yet. Start by uploading a file to hide in a chess game.
            </p>
            <div className="space-x-4">
              <a
                href="/encode"
                className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors inline-block"
              >
                Encode Your First File
              </a>
              <a
                href="/decode"
                className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors inline-block"
              >
                Decode a PGN File
              </a>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {userFiles.map((file) => (
              <div key={file.pgn_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-2xl">
                      {getFileTypeIcon(file.file_type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">
                        {file.original_filename}
                      </h3>
                      <div className="text-sm text-gray-600 space-x-4">
                        <span>Type: {file.file_type}</span>
                        <span>Created: {formatDate(file.created_at)}</span>
                      </div>
                      <div className="text-xs text-gray-500 font-mono mt-1">
                        ID: {file.pgn_id}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => downloadFile(file.pgn_id)}
                      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors text-sm"
                    >
                      Download PGN
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Wallet Security Info */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-xl font-semibold mb-4">Wallet Security</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-green-800 mb-2">✅ Current Security Status</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Wallet signature verified</li>
              <li>• X402 micropayment system active</li>
              <li>• Blockchain authentication enabled</li>
              <li>• File access controls enforced</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-blue-800 mb-2">🔐 Privacy Features</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Files encrypted in chess game format</li>
              <li>• No personal data stored on server</li>
              <li>• Wallet-based access control</li>
              <li>• Self-destructing message support</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <span className="text-yellow-500">⚠️</span>
            <div>
              <h4 className="font-semibold text-yellow-800">Security Reminder</h4>
              <p className="text-yellow-700 text-sm mt-1">
                Keep your wallet secure and never share your private keys. All operations require wallet signatures for verification.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletConnect;
