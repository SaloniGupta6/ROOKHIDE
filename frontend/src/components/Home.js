import React from 'react';

const Home = ({ walletConnected, walletAddress, onTabChange }) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-gray-800 mb-4">
          ChessCrypt DApp
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Hide secret messages in chess games using blockchain-secured steganography
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-blue-800 mb-4">
            🔐 Secure • 🎮 Playable • 🌐 Decentralized
          </h2>
          <p className="text-blue-700">
            Combine the ancient game of chess with modern cryptography and blockchain technology
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="text-xl font-semibold mb-3">Encode Messages</h3>
          <p className="text-gray-600 mb-4">
            Hide your secret messages inside valid PGN chess games. Each move carries hidden data while maintaining a playable game.
          </p>
          <button
            onClick={() => onTabChange && onTabChange('encode')}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors inline-block"
          >
            Start Encoding
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-4xl mb-4">🔓</div>
          <h3 className="text-xl font-semibold mb-3">Decode Messages</h3>
          <p className="text-gray-600 mb-4">
            Extract hidden messages from PGN files. Verify authenticity through blockchain and retrieve your secret data.
          </p>
          <button
            onClick={() => onTabChange && onTabChange('decode')}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors inline-block"
          >
            Start Decoding
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h2 className="text-2xl font-semibold mb-6 text-center">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">1️⃣</span>
            </div>
            <h3 className="font-semibold mb-2">Connect Wallet</h3>
            <p className="text-sm text-gray-600">
              Connect your Coinbase Wallet to authenticate and enable blockchain features
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">2️⃣</span>
            </div>
            <h3 className="font-semibold mb-2">Pay & Process</h3>
            <p className="text-sm text-gray-600">
              Make a small micropayment via X402 protocol to encode/decode your message
            </p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">3️⃣</span>
            </div>
            <h3 className="font-semibold mb-2">Share & Play</h3>
            <p className="text-sm text-gray-600">
              Download your PGN file - it's a valid chess game that can be played anywhere
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Features</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>Chess-based steganography</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>Coinbase Wallet integration</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>X402 micropayments</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>Valid playable chess games</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>Self-destructing messages</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-500">✓</span>
            <span>Open-source & free</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;