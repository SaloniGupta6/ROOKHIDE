import React from 'react';
import { Link } from 'react-router-dom';

const Header = ({ walletConnected, walletAddress, onConnect, onDisconnect }) => {
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <header className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-2xl font-bold text-gray-800">
              ♟️ ChessCrypt
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link to="/" className="text-gray-600 hover:text-gray-800">
                Home
              </Link>
              <Link to="/encode" className="text-gray-600 hover:text-gray-800">
                Encode
              </Link>
              <Link to="/decode" className="text-gray-600 hover:text-gray-800">
                Decode
              </Link>
              <Link to="/visualizer" className="text-gray-600 hover:text-gray-800">
                Visualizer
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            {walletConnected ? (
              <div className="flex items-center space-x-2">
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                  🟢 {formatAddress(walletAddress)}
                </div>
                <button
                  onClick={onDisconnect}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <button
                onClick={onConnect}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
              >
                Connect Wallet
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;