import React, { useState } from 'react';
import './App.css';

// Simple components without complex crypto dependencies
import Home from './components/Home';
import Encode from './components/Encode';
import Decode from './components/Decode';


function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');

  const connectWallet = async () => {
    try {
      if (typeof window.ethereum !== 'undefined') {
        // Request account access
        const accounts = await window.ethereum.request({ 
          method: 'eth_requestAccounts' 
        });
        
        if (accounts.length > 0) {
          const address = accounts[0];
          setWalletAddress(address);
          setWalletConnected(true);
          
          // Test backend authentication
          try {
            const message = `Connect to ChessCrypt DApp at ${Date.now()}`;
            const signature = await window.ethereum.request({
              method: 'personal_sign',
              params: [message, address]
            });

            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/wallet/connect`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                wallet_address: address,
                signature: signature,
                message: message
              })
            });

            const data = await response.json();
            if (data.success) {
              alert(`✅ Coinbase Wallet connected successfully!\nAddress: ${address.substring(0, 10)}...\nAuthenticated with backend.`);
            } else {
              alert(`⚠️ Wallet connected but backend authentication failed: ${data.error}`);
            }
          } catch (authError) {
            console.error('Backend authentication failed:', authError);
            alert(`⚠️ Wallet connected but backend authentication failed. You can still use the DApp.`);
          }
        }
      } else {
        alert('❌ Coinbase Wallet not found!\n\nPlease install the Coinbase Wallet browser extension:\nhttps://wallet.coinbase.com/');
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
      if (error.code === 4001) {
        alert('❌ Wallet connection rejected by user.');
      } else {
        alert(`❌ Wallet connection failed: ${error.message}`);
      }
    }
  };

  const disconnectWallet = () => {
    setWalletConnected(false);
    setWalletAddress('');
    alert('Wallet disconnected');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">
                ♟️ ChessCrypt DApp
              </h1>
              <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                v1.0.0
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              {walletConnected ? (
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">
                      {walletAddress.substring(0, 6)}...{walletAddress.substring(38)}
                    </span>
                  </div>
                  <button
                    onClick={disconnectWallet}
                    className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Disconnect
                  </button>
                </div>
              ) : (
                <button
                  onClick={connectWallet}
                  className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Connect Wallet
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
          {[
  { id: 'home', label: 'Home', icon: '🏠' },
  { id: 'encode', label: 'Encode', icon: '🔐' },
  { id: 'decode', label: 'Decode', icon: '🔓' },
  
].map((tab) => (

              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeTab === 'home' && (
            <Home 
              walletConnected={walletConnected}
              walletAddress={walletAddress}
              onTabChange={setActiveTab}
            />
          )}
          {activeTab === 'encode' && (
            <Encode 
              walletConnected={walletConnected}
              walletAddress={walletAddress}
            />
          )}
          {activeTab === 'decode' && (
            <Decode 
              walletConnected={walletConnected}
              walletAddress={walletAddress}
            />
          )}


        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">ChessCrypt DApp</h3>
              <p className="text-gray-300">
                Hide secret messages in chess games using advanced steganography and blockchain technology.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Features</h3>
              <ul className="text-gray-300 space-y-2">
                <li>• Chess steganography encoding</li>
                <li>• Coinbase Wallet integration</li>
                <li>• X402 micropayments</li>
                <li>• Blockchain security</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Status</h3>
              <div className="text-gray-300 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Backend API: Online</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Frontend: Online</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${walletConnected ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                  <span>Wallet: {walletConnected ? 'Connected' : 'Disconnected'}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
            <p>&copy; 2025 ChessCrypt DApp. Decentralized chess steganography platform.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;